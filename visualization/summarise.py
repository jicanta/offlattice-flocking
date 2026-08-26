"""Resume el barrido en una tabla: un registro por caso (modelo, rho, eta).

Para cada caso apila las M realizaciones, determina t_eq sobre la curva
promedio de va(t) y calcula el valor medio y el desvio estandar de va y de S
sobre todas las muestras estacionarias (ver common.analyse_case). El resultado
va a data/sweep/resumen.csv, que es lo unico que leen las curvas de los items
(c), (d), (e) y (f): asi todas salen del mismo calculo.

    python3 visualization/summarise.py
"""

from __future__ import annotations

import argparse

import common


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    grouped = common.group_runs(common.read_index(arguments.sweep))
    records = []
    pending = []
    for (model, rho, eta), group in sorted(grouped.items()):
        stack = common.load_case(group)
        result = common.analyse_case(stack)
        if not result["converged"]:
            pending.append((model, rho, eta))
        records.append(
            {
                "model": model,
                "rho": rho,
                "N": group[0]["N"],
                "eta": eta,
                "M": result["M"],
                "steps": group[0]["steps"],
                "teq": result["teq"],
                "va": result["va"],
                "va_std": result["va_std"],
                "S": result["S"],
                "S_std": result["S_std"],
                "converged": result["converged"],
            }
        )
        print(f"{model:6s} rho={rho:g} eta={eta:<5g} M={result['M']:2d} "
              f"teq={result['teq']:6.0f}  va={result['va']:.4f} ± {result['va_std']:.4f}  "
              f"S={result['S']:.4f} ± {result['S_std']:.4f}")

    if pending:
        print(f"aviso: {len(pending)} casos cuya curva promedio todavia deriva en el "
              "ultimo cuarto (hacen falta mas pasos):")
        for model, rho, eta in pending:
            print(f"  {model} rho={rho:g} eta={eta:g}")
    common.write_summary(records, arguments.sweep / "resumen.csv")


if __name__ == "__main__":
    main()
