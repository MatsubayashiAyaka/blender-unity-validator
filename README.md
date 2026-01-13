# Unity Export Validator for Blender

![Blender](https://img.shields.io/badge/Blender-3.6%2B-orange)
![License](https://img.shields.io/badge/License-GPL--3.0-blue)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)

A Blender addon that validates 3D assets before exporting to Unity (URP), helping artists catch common issues that cause problems in Unity.

## Features

- **Transform Validation**: Detect unapplied scale, rotation, and negative scale
- **Material Validation**: Find missing materials and empty material slots
- **UV Validation**: Check for missing UV maps
- **Geometry Validation**: Detect N-gons and inverted faces
- **Naming Validation**: Find problematic object names (spaces, Japanese characters, default names)
- **Severity Levels**: Error, Warning, and Info classifications
- **One-Click Selection**: Click on any issue to select the problematic object

## Screenshots

<!-- TODO: Add screenshots -->

## Requirements

- Blender 3.6 or later (tested on 4.2)
- Windows / macOS / Linux

## Installation

1. Download the latest release from [Releases](../../releases)
2. In Blender, go to `Edit` → `Preferences` → `Add-ons`
3. Click `Install...` and select the downloaded `.zip` file
4. Enable the addon by checking the checkbox

## Usage

1. Open the `View3D` sidebar (`N` key)
2. Find the `Unity Validator` tab
3. Click `Run Validation`
4. Review and fix any issues

For detailed usage, see [Documentation](docs/USAGE.md).

## Architecture

This addon follows a modular architecture for easy extension:

- **Checker Pattern**: Each validation rule is a separate checker class
- **Registry System**: Checkers are auto-registered via decorators
- **Version Compatibility**: Abstraction layer for Blender API differences

For technical details, see [Architecture](docs/ARCHITECTURE.md).

## Roadmap

- [ ] Phase 1: Core validation (Transform, Material, UV)
- [ ] Phase 2: Geometry validation (N-gon, Face Orientation)
- [ ] Phase 3: Export integration and presets

## Contributing

Contributions are welcome! Please read the contribution guidelines before submitting a PR.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Author

## TODO
- Portfolio: [your-portfolio-url]
- GitHub: https://github.com/MatsubayashiAyaka/blender-unity-validator.git

---

*This addon was created as a portfolio piece demonstrating Technical Artist skills in tool development.*