# DeepSeek OCR Ollama
This is a simple script that uses the Ollama API to get the Markdown text from a PDF or image file using the [DeepSeek-OCR](https://arxiv.org/pdf/2510.18234) model

# Usage

## Install the Requirements

To install the necessary requirements, run the following command:

```sh
pip install deepseek-ocr-ollama
```

To be used, [Ollama](https://ollama.com/download) is required and the deepseek-ocr model must be installed

```sh
ollama pull deepseek-ocr
```

## Typical Usage

```sh
deepseek-ocr-ollama paper.pdf
deepseek-ocr-ollama paper.pdf --dpi 200
deepseek-ocr-ollama paper.pdf -o revision
deepseek-ocr-ollama paper.pdf -e
deepseek-ocr-ollama paper.pdf -m FULL
deepseek-ocr-ollama page74.jpg -e
deepseek-ocr-ollama OLLAMA_HOST=http://gauss:11434 receipt.pdf -e
deepseek-ocr-ollama -j paper.json
deepseek-ocr-ollama -j paper.json -m TEXT_NO_PAGES -n
```

## Arguments

| Argument || Description |
|-|-|-|
| | input | input PDF or image file |
| -d DPI | --dpi DPI | DPI (dots per inch) setting for the PDF to image conversion. Defaults to 600 |
| -o OUTPUT | --output OUTPUT | output directory path. If not set, a directory will be created in the current working directory using the same stem (filename without extension) as the input file |
| -j JSON_OCR_RESPONSE | --json-ocr-response JSON_OCR_RESPONSE | path from which to load a pre-existing JSON OCR response (any input file will be ignored) |
| -m MODE | --mode MODE | mode of operation: either the name or numerical value of the mode. _Defaults to FULL_NO_PAGES_ |
| -s PAGE_SEPARATOR | --page-separator PAGE_SEPARATOR | page separator to use when writing the Markdown file. _Defaults to `\n`_ |
| -n | --no-json | do not write the JSON OCR response to a file. By default, the response is written |
| -e | --load-dot-env | load the .env file from the current directory using [`python-dotenv`](https://pypi.org/project/python-dotenv/), to retrieve the Ollama environment variables |
| -E LOAD_PATH_DOT_ENV | --load-path-dot-env LOAD_PATH_DOT_ENV | load the .env file from the specified path using [`python-dotenv`](https://pypi.org/project/python-dotenv/), to retrieve the Ollama environment variables. Defaults to ~/.deepseek_ocr_ollama.env |
| -M MODEL_NAME | --model-name MODEL_NAME | name of the Ollama model to use for OCR. Defaults to [`deepseek-ocr`](https://ollama.com/library/deepseek-ocr) |
| -H HINT | --hint HINT | hint to provide to the OCR model to improve recognition accuracy. Ignored if raw prompt is set. The hint is a short instruction that will be mixed in with the main prompt |
| -R RAW_PROMPT | --raw-prompt RAW_PROMPT | raw prompt to provide to the OCR model, overriding the default prompt. Hint is ignored if this is set |
| -V VERBOSE | --verbose VERBOSE | verbosity level: 0 = silent, 1 = normal, 2 = debug. Defaults to 1 |


## Modes

| Value | Name |
|-|-|
| 0 | FULL |
| 1 | FULL_ALT |
| 2 | FULL_NO_DIR |
| 3 | FULL_NO_PAGES |
| 4 | TEXT |
| 5 | TEXT_NO_PAGES |

Given the input file `paper.pdf`, the directory structure for each mode is shown below:

### 0 - `FULL`

Structure
```
paper
├── full
│   ├── image1.png
│   ├── image2.png
│   ├── image3.png
│   └── paper.md
├── page_0
│   ├── image1.png
│   └── paper.md
├── page_1
│   ├── image2.png
│   └── paper.md
└── page_2
    ├── image3.png
    └── paper.md
```

### 1 - `FULL_ALT`

Structure
```
paper
├── image1.png
├── image2.png
├── image3.png
├── paper.md
├── page_0
│   ├── image1.png
│   └── paper.md
├── page_1
│   ├── image2.png
│   └── paper.md
└── page_2
    ├── image3.png
    └── paper.md
```

### 2 - `FULL_NO_DIR`

Structure
```
paper
├── image1.png
├── image2.png
├── image3.png
├── paper.md
├── paper0.md
├── paper1.md
└── paper2.md
```

### 3 - `FULL_NO_PAGES` *default*

Structure
```
paper
├── image1.png
├── image2.png
├── image3.png
└── paper.md
```

### 4 - `TEXT`

Structure
```
paper
├── paper.md
├── paper0.md
├── paper1.md
└── paper2.md
```

### 5 - `TEXT_NO_PAGES`

Structure
```
paper
└── paper.md
```

By default, the JSON response from the DeepSeek-OCR model is saved in the output directory. To disable JSON output, use the `-n` or `--no-json` argument. To experiment with a different **mode** without using additional calls, reuse an existing JSON response instead of the original input file

### Ollama's Environment Variables

The Ollama server can be modified using the environment variables available from the [Python API](https://github.com/ollama/ollama-python):

- **OLLAMA_HOST** : Ollama server host
- **OLLAMA_API_KEY** : Used as Bearer authorization token

To avoid using `-e` to load the `.env` file, you can create one at `$HOME/.deepseek_ocr_ollama.env` (where `$HOME` is your home directory). It will then be automatically loaded at the start of the script

For example, for an user called `vavilov`, the path would look like this:

* **Linux**
  ```
  /home/vavilov/.deepseek_ocr_ollama.env  
  ```

* **macOS**
  ```
  /Users/vavilov/.deepseek_ocr_ollama.env  
  ```

* **Windows**
  ```
  C:\Users\vavilov\.deepseek_ocr_ollama.env  
  ```

and the content will be something like this:

```
OLLAMA_HOST=http://gauss:11434
```
