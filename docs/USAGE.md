# Usage Guide

## Basic Usage

1. Select objects to validate (or validate all mesh objects)
2. Open the sidebar panel (`N` key in 3D Viewport)
3. Navigate to the `Unity Validator` tab
4. Click `Run Validation`

## Understanding Results

### Severity Levels

| Icon | Level | Meaning |
|------|-------|---------|
| 🔴 | Error | Must fix before export |
| 🟡 | Warning | Should fix, may cause issues |
| 🔵 | Info | Recommendation only |

### Validation Categories

#### Transform
- **Negative Scale**: Will cause inverted normals in Unity
- **Unapplied Transform**: May cause unexpected behavior

#### Materials
- **No Material**: Object will appear pink/magenta in Unity
- **Empty Slot**: Unused material slot detected

#### UV
- **No UV Map**: Required for texturing in Unity

## Excluding Objects

To exclude an object from specific checks:

1. Select the object
2. In Properties panel, find `Custom Properties`
3. Add: `unity_validator_exclude_[checker_name] = True`

## Settings

Access addon preferences via `Edit` → `Preferences` → `Add-ons` → `Unity Validator`