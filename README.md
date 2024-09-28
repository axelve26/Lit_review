This directory contains the code for the systematic literature review: 'Harnassing the power of artificial intelligence to generate adverse outcome pathways from existing literature'. The code is written in Python and uses the Dash library to create a web-based interface to facilitate the review process.
1. Download the folder and use cd to navigate to it:
```bash
git clone https://github.com/axelve26/Lit_review.git
cd ./Lit_review_code
```
2. Create the lit_review environment with Conda based on the provided yaml file:
```bash
conda env create -f Lit_review_environment.yml
```
3. Activate the environment:
```bash
conda activate lit_review
```
4. Run the script with the command:
```bash
python Lit_review.py
```
Notes:
- The clickable link on top of the Dash app will redirect to the article. Hold `Ctrl` and click to open in a new tab. Hold `Shift` and click to open in a new window. Additionally, after opening the article in a new window, this window can be placed on the right side of the screen by pressing `Windows` + `Right arrow` and the Dash app can be placed on the left side of the screen by pressing `Enter`. 
- In the Dash app, progress can be saved by clicking the "Save progress" button. Such progress is loaded automatically (if present) when the Dash app is started. The progress is saved in the saved_progress folder by its Pubmed_ID (e.g. `save_in_progress_<Pubmed_ID>.json`).
- Provided sentences in both the "relevant citations" and "what2write" fields should be separated by two dots ".." (not followed by a space in case of "relevant citations"), except for the last sentence which should have no dot at the end.
- When you want to stop the Dash app, you can press `Ctrl + C` in the terminal. In case you didn't use `Ctrl + C` but e.g. `Ctrl + z`, you can check which process is using the port 8050 with:
```bash
lsof -i :8050
```
In the second column you will see the PID of the process that is using the port 8050. You can kill the process with the command:
```bash
kill -9 <PID>
```
- Clickable links to the citations are provided in the 'included_articles.csv' file. This only works in Chrome. They may malfunction if there is no PMC ID and no API key is provided to obtain the pii from Elsevier in a separate csv.
