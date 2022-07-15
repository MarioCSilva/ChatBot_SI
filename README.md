# Chatbot

Project developed under the course of Inteligent Systems.

## How to run

From the `src` directory, run the following commands on a terminal to install dependencies:

    pip install -r src/requirements.txt

    python3 -m spacy download en_core_web_md

    mvn dependency:copy-dependencies -DoutputDirectory=./jars -f $(python3 -c 'import importlib; import pathlib; print(pathlib.Path(importlib.util.find_spec("sutime").origin).parent / "pom.xml")')

From the same directory, execute the program:

    python3 main.py