from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import torch
from alignn.graphs import Graph
from alignn.models.alignn_atomwise import ALIGNNAtomWise, ALIGNNAtomWiseConfig
from jarvis.core.atoms import Atoms
from pymatgen.ext.matproj import MPRester


def extract_prediction(output):
    if torch.is_tensor(output):
        return output.detach().cpu().numpy().flatten().tolist()[0]
    if isinstance(output, dict):
        for key in ("graphwise_pred", "out", "output", "prediction"):
            value = output.get(key)
            if torch.is_tensor(value):
                return value.detach().cpu().numpy().flatten().tolist()[0]
        for value in output.values():
            if torch.is_tensor(value):
                return value.detach().cpu().numpy().flatten().tolist()[0]
    raise RuntimeError(f"Unsupported model output type: {type(output)}")


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("Usage: predict_solid_alignn.py <formula> <model_path> <config_path> <api_key>")

    formula, model_path, config_path, api_key = sys.argv[1:]
    model_path = Path(model_path)
    config_path = Path(config_path)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    with config_path.open("r", encoding="utf-8") as handle:
        config_data = json.load(handle)

    model = ALIGNNAtomWise(ALIGNNAtomWiseConfig(**config_data["model"]))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    with MPRester(api_key) as mpr:
        material_ids = mpr.get_material_ids(formula)
        if not material_ids:
            raise SystemExit(f"No Materials Project structure found for formula: {formula}")
        material_id = str(material_ids[0])
        structure = mpr.get_structure_by_material_id(material_id)

    with tempfile.TemporaryDirectory() as temp_dir:
        poscar_path = Path(temp_dir) / f"{material_id}.vasp"
        structure.to(filename=str(poscar_path), fmt="poscar")
        atoms = Atoms.from_poscar(str(poscar_path))
        graph, line_graph = Graph.atom_dgl_multigraph(atoms)
        lattice = torch.tensor(atoms.lattice_mat)
        output = model([graph.to(device), line_graph.to(device), lattice.to(device)])
        prediction = extract_prediction(output)

    print(
        json.dumps(
            {
                "prediction": float(prediction),
                "material_id": material_id,
                "formula": formula,
                "weight_source": str(model_path.name),
            }
        )
    )


if __name__ == "__main__":
    main()
