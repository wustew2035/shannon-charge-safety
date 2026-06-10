# Shannon Charge Safety Calculator

Python package and command-line tool to calculate electrical stimulation:

- **Charge per phase** in `uC/phase`
- **Charge density** in `uC/cm^2/phase`
- **Shannon k value** using `k = log10(Q) + log10(D)`

where `Q` is charge per phase in `uC/phase` and `D` is charge density in `uC/cm^2/phase`.

> Safety note: This tool is for research/engineering calculation support only. It does **not** determine clinical safety, device compliance, or regulatory acceptability. Always verify electrode geometry, waveform assumptions, manufacturer guidance, and protocol-specific limits.

## Install

### Direct install from GitHub

You can install directly from GitHub without manually cloning the repository:

```bash
python -m pip install git+https://github.com/wustew2035/shannon-charge-safety.git
```

To upgrade later:

```bash
python -m pip install --upgrade git+https://github.com/wustew2035/shannon-charge-safety.git
```

### Editable/development install

Use this option only if you want a local editable copy for development:

```bash
git clone https://github.com/wustew2035/shannon-charge-safety.git
cd shannon-charge-safety
python -m pip install -e .
```


## Command-line usage

Required stimulation inputs:

- `--current-ma`: current in mA
- `--pulse-width-us`: pulse width in microseconds

You can enter electrode surface area in either of two ways.

### Option 1: cylinder diameter and height in mm

Use this when the exposed electrode surface is the lateral surface of a cylindrical contact:

```bash
shannon-charge-safety --current-ma 6 --pulse-width-us 60 --diameter-mm 1.36 --height-mm 1.5
```

This calculates area as:

```text
surface_area_mm2 = pi * diameter_mm * height_mm
```

Example output:

```text
Charge safety calculation
-------------------------
Current:               6 mA
Pulse width:           60 us
Surface area:          6.40885 mm^2 (0.0640885 cm^2)
Charge per phase:      0.36 uC/phase
Charge density:        5.61723 uC/cm^2/phase
Shannon k:             0.305825
```

### Medtronic segmented-lead modifier

You can add `--medtronic-segment 1` or `--medtronic-segment 2` to approximate the active conductive-arc fraction for Medtronic segmented DBS lead models B33005 and B33015. This works with either input style: `--diameter-mm`/`--height-mm` or `--surface-area-mm2`. In these leads, each segmented level has 3 segments with a 100° conductive arc per segment, separated by 20° gaps. Therefore:

- `--medtronic-segment 1` multiplies the selected area by `100/360 = 5/18`.
- `--medtronic-segment 2` multiplies the selected area by `200/360 = 5/9`.

Example for one active Medtronic segment using cylinder dimensions:

```bash
shannon-charge-safety --current-ma 6 --pulse-width-us 60 --diameter-mm 1.36 --height-mm 1.5 --medtronic-segment 1
```

Example for one active Medtronic segment when entering the full ring/level surface area directly:

```bash
shannon-charge-safety --current-ma 6 --pulse-width-us 60 --surface-area-mm2 6.41 --medtronic-segment 1
```

If your `--surface-area-mm2` value already represents the final active segmented-contact area, do **not** also use `--medtronic-segment`; otherwise the area will be fraction-scaled twice.

### Option 2: surface area as a single value in mm²

Use this when you already know the exposed electrode surface area:

```bash
shannon-charge-safety --current-ma 6 --pulse-width-us 60 --surface-area-mm2 6.41
```

### JSON output

```bash
shannon-charge-safety --current-ma 6 --pulse-width-us 60 --surface-area-mm2 6.41 --json
```

## Python usage

```python
from shannon_charge_safety import calculate_charge_safety

# Area input option 1: cylinder diameter and height in mm
# medtronic_segment=1 applies the one-segment area fraction, 5/18.
result = calculate_charge_safety(
    current_mA=6,
    pulse_width_us=60,
    diameter_mm=1.36,
    height_mm=1.5,
    medtronic_segment=1,
)
print(result.charge_density_uC_per_cm2)
print(result.shannon_k)

# Area input option 2: surface area in mm^2
# Python name mirrors the CLI flag --surface-area-mm2.
# medtronic_segment=1 treats 6.41 mm^2 as the full ring/level area,
# then applies the one-segment area fraction, 5/18.
result = calculate_charge_safety(
    current_mA=6,
    pulse_width_us=60,
    surface_area_mm2=6.41,
    medtronic_segment=1,
)
```

## Equations

### Charge per phase

```text
Q_uC = current_mA * pulse_width_us / 1000
```

### Area conversion

```text
surface_area_cm2 = surface_area_mm2 / 100
```

### Charge density

```text
D = Q_uC / surface_area_cm2
```

### Shannon k value

```text
k = log10(Q_uC) + log10(D)
```

## Example: 1.36 mm diameter × 1.5 mm height cylindrical contact

```bash
shannon-charge-safety --current-ma 6 --pulse-width-us 60 --diameter-mm 1.36 --height-mm 1.5
```

This gives:

- Surface area: `6.41 mm^2 = 0.0641 cm^2`
- Charge per phase: `0.36 uC/phase`
- Charge density: approximately `5.62 uC/cm^2/phase`
- Shannon k: approximately `0.306`

## Important geometry caveat

For cylindrical ring contacts, `--diameter-mm` and `--height-mm` use the lateral cylindrical surface area: `pi × diameter_mm × height_mm`. This excludes the circular end caps. For Medtronic B33005/B33015 segmented contacts, `--medtronic-segment` applies the 100°-arc segment fraction to the selected area, whether that area was calculated from dimensions or supplied with `--surface-area-mm2`. Use `--surface-area-mm2` when you already know the manufacturer-specified surface area or when the contact geometry is rectangular or otherwise non-cylindrical. If that supplied value is already the final active segmented area, omit `--medtronic-segment`.

## Shannon k value safety

![Shannon k value safety](assets/k_safety.jpg)

**Figure.** Exceeding a Shannon k value of 1.85 may cause neural tissue damage. Figure is from Cogan et al. 2017.

## Citations

- Cogan et al. Tissue damage thresholds during therapeutic electrical stimulation. Journal of Neural Engineering. 2016 Apr;13(2):021001. doi: 10.1088/1741-2560/13/2/021001.
- Shannon RV. A model of safe levels for electrical stimulation. IEEE Transactions on Biomedical Engineering. 1992 Apr;39(4):424-6. doi: 10.1109/10.126616.
- McCreery et al. Charge density and charge per phase as cofactors in neural injury induced by electrical stimulation. IEEE Transactions on Biomedical Engineering. 1990 Oct;37(10):996-1001. doi: 10.1109/10.102812.
- McCreery et al. Comparison of neural damage induced by electrical stimulation with faradaic and capacitor electrodes. Annals of Biomedical Engineering. 1988;16(5):463-81. doi: 10.1007/BF02368010.

## License

MIT
