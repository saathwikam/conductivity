# Solid ALIGNN Training

This is the current practical path to start true ALIGNN training for the solid dataset.

## 1. Create a Python 3.10 environment

Use conda if possible:

```powershell
conda create -n alignn310 python=3.10 -y
conda activate alignn310
```

## 2. Install ALIGNN stack

```powershell
pip install torch torchvision torchaudio
pip install dgl
pip install pandas pymatgen
pip install git+https://github.com/usnistgov/alignn.git
```

## 3. Set your Materials Project API key

Do not hardcode it into files. Set it only in the shell:

```powershell
$env:MP_API_KEY="YOUR_KEY_HERE"
```

## 4. Prepare ALIGNN-style training data

From the project root:

```powershell
python training\scripts\prepare_solid_alignn_data.py
```

This will create:

- `training/solid_alignn_data/structures/*.cif`
- `training/solid_alignn_data/id_prop.csv`
- `training/solid_alignn_data/missing_formulas.txt`

## 5. Train the solid model

```powershell
train_alignn.py --root_dir "training/solid_alignn_data" --config "training/solid_alignn_config.json" --output_dir "models/solid_alignn_training"
```

## 6. Promote the best checkpoint

After training finishes, copy the best model into:

- `models/alignn_solid.pth`

## Notes

- Some formulas may not map directly to a Materials Project structure.
- Doped or disordered compositions may need manual structure curation.
- This process is suitable for the solid dataset only.
- The liquid dataset still needs a separate structure-rich representation before ALIGNN-style training is realistic.
