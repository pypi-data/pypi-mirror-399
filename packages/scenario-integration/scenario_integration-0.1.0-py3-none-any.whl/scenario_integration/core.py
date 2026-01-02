from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import numpy as np
import textwrap

# -------- public helper --------
STATE_COLS: list[str] = []  # will be set after first enforce_schema call

def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    global STATE_COLS
    if "weather_datetime" in df.columns:
        df["weather_datetime"] = pd.to_datetime(df["weather_datetime"], errors="coerce")
    # infer state cols (anything not meta)
    meta = {"sector", "subsector", "dispatch_feeder", "weather_datetime", "weather_year"}
    STATE_COLS = [c for c in df.columns if c not in meta]
    for c in STATE_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df[STATE_COLS] = df[STATE_COLS].fillna(0.0)
    for c in ("sector", "subsector", "dispatch_feeder"):
        if c in df.columns:
            df[c] = df[c].astype("category")
    return df

# -------- package API --------
@dataclass
class ScenarioIntegrator:
    """Notebook-friendly wrapper. Fill in real logic next."""
    data_root: Path = Path("./files")

    # step 1 placeholder
    def process(
        self,
        *,
        year: int,
        scenario: str,
        custom_values: dict | None = None,
        fallback_scenarios: dict | None = None,
        state_base_scenarios: dict | None = None,
        shed_shift_enabled: dict | None = None,
        diagnostics: bool = False,
    ) -> pd.DataFrame:
        import gc
        import pandas as pd
        from pathlib import Path

        custom_values = custom_values or {}
        fallback_scenarios = fallback_scenarios or {}
        state_base_scenarios = { (k or "").strip().lower(): v for k, v in (state_base_scenarios or {}).items() }
        shed_shift_enabled = shed_shift_enabled or {}

        # --- helpers ---
        def _optimize(df: pd.DataFrame) -> pd.DataFrame:
            for col in df.select_dtypes(include=["object"]).columns:
                if col in ["subsector","sector","dispatch_feeder"]:
                    df[col] = df[col].astype("category")
            for col in df.select_dtypes(include=["int64","int32","int16","int8"]).columns:
                df[col] = pd.to_numeric(df[col], downcast="integer")
            for col in df.select_dtypes(include=["float64","float32"]).columns:
                df[col] = pd.to_numeric(df[col], downcast="float")
            return df

        def _load(scen: str, cols=None) -> pd.DataFrame:
            p = self.data_root / f"{year}_{scen}.csv.gz"
            if not p.exists():
                raise FileNotFoundError(f"File not found: {p}")
            df = pd.read_csv(p, usecols=cols, low_memory=False)
            return _optimize(df)

        # --- base ---
        gc.collect()
        full_df = _load(scenario)
        orig_set = set(full_df["subsector"].astype(str).str.strip().str.lower().unique())

        # keep common types
        full_df["weather_datetime"] = pd.to_datetime(full_df["weather_datetime"], errors="coerce")
        full_df = full_df.dropna(subset=["weather_datetime"])

        # --- per-state base overrides ---
        for state, state_scen in state_base_scenarios.items():
            if state == "__all_states__" or state_scen == scenario:
                continue
            if state not in full_df.columns:
                continue
            need = ["subsector","weather_datetime", state]
            sdf = _load(state_scen, cols=need)
            mask_cols = (sdf["subsector"].astype(str).str.strip().str.lower()
                        .isin(full_df["subsector"].astype(str).str.strip().str.lower().unique()))
            if not mask_cols.any():
                continue
            mapping = dict(zip(pd.to_datetime(sdf["weather_datetime"], errors="coerce"), sdf[state]))
            m = full_df["weather_datetime"].map(mapping)
            full_df.loc[:, state] = m.fillna(full_df[state])

        # --- fallback per (state, subsector) ---
        parsed_fb: dict[tuple[str,str], str] = {}
        for k, v in fallback_scenarios.items():
            if isinstance(k, str):
                parts = [t.strip() for t in k.split(",")]
                if len(parts) >= 2:
                    parsed_fb[(parts[0].lower(), ",".join(parts[1:]))] = v
            else:
                parsed_fb[k] = v

        for (state, subsector), fb_scen in parsed_fb.items():
            ss_mask = full_df["subsector"].astype(str).str.strip().str.lower().eq(subsector.strip().lower())
            if not ss_mask.any():
                continue
            fb_df = _load(fb_scen)
            fb_df["weather_datetime"] = pd.to_datetime(fb_df["weather_datetime"], errors="coerce")
            fb_df = fb_df[fb_df["subsector"].astype(str).str.strip().str.lower().eq(subsector.strip().lower())]
            if state == "__all_states__":
                full_df = full_df[~ss_mask]
                full_df = pd.concat([full_df, fb_df], ignore_index=True)
            elif state in full_df.columns and state in fb_df.columns:
                map_state = dict(zip(fb_df["weather_datetime"], pd.to_numeric(fb_df[state], errors="coerce")))
                m = full_df.loc[ss_mask, "weather_datetime"].map(map_state)
                full_df.loc[ss_mask, state] = m.fillna(full_df.loc[ss_mask, state])

        # --- custom percentage tweaks per (state, subsector) ---
        parsed_cv: dict[tuple[str,str], float] = {}
        for k, v in custom_values.items():
            if isinstance(k, str):
                parts = [t.strip() for t in k.split(",")]
                if len(parts) >= 2:
                    parsed_cv[(parts[0].lower(), ",".join(parts[1:]))] = float(v)
            else:
                parsed_cv[k] = float(v)

        for (state, subsector), pct in parsed_cv.items():
            if pct == 0:
                continue
            mask = full_df["subsector"].astype(str).str.strip().str.lower().eq(subsector.strip().lower())
            if not mask.any():
                continue
            if state == "__all_states__":
                for col in full_df.columns:
                    if col not in ["weather_datetime","subsector","sector","dispatch_feeder","weather_year"]:
                        full_df.loc[mask, col] = pd.to_numeric(full_df.loc[mask, col], errors="coerce") * pct
            elif state in full_df.columns:
                full_df.loc[mask, state] = pd.to_numeric(full_df.loc[mask, state], errors="coerce") * pct

        # --- (optional) shed/shift — only if you later wire shed_shift_config on self ---
        # no-op here unless you add your config + logic

        # --- diagnostics or finalize ---
        final_set = set(full_df["subsector"].astype(str).str.strip().str.lower().unique())
        if diagnostics:
            return pd.DataFrame({
                "unique_in_count": [len(orig_set)],
                "unique_out_count": [len(final_set)],
                "missing_from_output": [sorted(orig_set - final_set)],
                "added_in_output": [sorted(final_set - orig_set)],
            })

        return enforce_schema(full_df)
    @property
    def help(self):
        """Pretty, pandas-style help on what you can tweak."""
        print("ScenarioIntegrator Help".ljust(80, "="))
        print("Main methods:\n")

        print("• process(year, scenario, *, ...)")
        print(textwrap.dedent("""
            - year: int
            - scenario: str ("baseline" | "central" | "conservative")
            - custom_values: dict[(state, subsector) -> float]
                  Example: {("texas","passenger car"): 1.10}
            - fallback_scenarios: dict[(state, subsector) -> scenario]
            - state_base_scenarios: dict[state -> scenario]
            - shed_shift_enabled: dict[state -> bool]
            - diagnostics: bool
        """).strip())

        print("\n• add_datacenter_capacity(year, base_year, *, ...)")
        print(textwrap.dedent("""
            - adding_MW: float = 100_000
                  Total MW to add across all states
            - cooling_prop_scenario: str
                  One of {"average","baseline","central","conservative"}
            - wy_scale_scenario: str
                  One of {"average","baseline","central","conservative"}
            - src_path: Path | None
                  Override input file location
        """).strip())

        print("\nData root (where CSVs live):")
        print(f"  {self.data_root.resolve()}")

        print("=" * 80)
        return None

    # step 2 placeholder
    def add_datacenter_capacity(
        self,
        *,
        year: int,
        base_year: int,
        adding_MW: float = 100_000.0,
        cooling_prop_scenario: str = "average",
        wy_scale_scenario: str = "average",
        src_path: str | Path | None = None,
    ) -> pd.DataFrame:
        # temporary: just echo the input file (so package imports fine)
        src = Path(src_path) if src_path else (self.data_root / f"{year}_custom_output.csv")
        df = pd.read_csv(src)
        return enforce_schema(df)

    def add_datacenter_capacity_to_csv(self, out_path: str | Path, **kwargs) -> str:
        df = self.add_datacenter_capacity(**kwargs)
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, index=False)
        return str(out_path)
