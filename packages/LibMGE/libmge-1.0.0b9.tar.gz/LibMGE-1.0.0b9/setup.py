from setuptools import setup

def get_long_description():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Configuração
setup(
    name="LibMGE",
    version="1.0.0b9",
    license="Zlib",

    # Descrições
    description="LibMGE is a powerful graphical user interface library for developing 2D programs and games.",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",

    # Autor
    author="Lucas Guimarães",
    author_email="commercial@lucasguimaraes.pro",

    # URLs
    url="https://libmge.org/",
    project_urls={
        "Source": "https://github.com/MonumentalGames/LibMGE",
        "Documentation": "https://docs.libmge.org/",
        "Bug Tracker": "https://github.com/MonumentalGames/LibMGE/issues",
        "Author Website": "https://lucasguimaraes.pro/"
    },

    # Requisitos
    python_requires=">=3.5",

    packages=[
        "LibMGE",
        "LibMGE/_sdl",
        "LibMGE/_InputsEmulator",
        "LibMGE/_ConsoleScripts"
    ],

    include_package_data=True,
    package_data={
        "LibMGE": [
            "*.dll",
            "*.so",
            "*.pyd",
            "*.pyi",
            "*.cpp",
            "*.h",
            "_sdl/*",
        ]
    },

    # Dependências
    install_requires=[
        "numpy",
    ],

    # Classificadores
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: zlib/libpng License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],

    # Scripts de console
    entry_points={
        "console_scripts": [
            "libmge=LibMGE._ConsoleScripts:main",
            "LibMGE=LibMGE._ConsoleScripts:main",
        ],
    },

    keywords=[
        "2D",
        "game development",
        "graphics",
        "GUI",
        "SDL",
        "game engine",
        "graphics library",
        "animation",
    ],

    # Metadados adicionais
    zip_safe=False,  # Importante para pacotes com arquivos binários
)
