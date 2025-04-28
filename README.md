# KeyStalker

A toolkit for detecting and analyzing API key leaks in browser extensions.

## Project Structure

```
KeyStalker/
├── extracting/      # Stage 1: Manifest analysis and network request detection
├── construction/    # Stage 2: PDG construction and AST analysis
├── detection/       # Stage 3: Entropy-based key detection
├── identification/  # Stage 4: API key verification and risk assessment
├── requirements.txt # Project dependencies
├── .gitignore      # Git ignore file
└── README.md       # Project documentation
```

## Functional Modules

- [x] Extraction: Manifest analysis and network request detection
- [ ] Construction: PDG construction and AST analysis
- [ ] Detection: Entropy-based key detection
- [ ] Identification: API key verification and risk assessment

## Installation

1. Clone the repository:
```bash
git clone https://github.com/KeyStalker2025/KeyStalker.git
cd KeyStalker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

For detailed usage instructions, please refer to the README file in each module's directory:

- [Extraction Module](extracting/README.md)
- [Construction Module](construction/README.md)
- [Detection Module](detection/README.md)
- [Identification Module](identification/README.md)

## Contributing

We welcome issues and improvements! Please follow these steps:

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
