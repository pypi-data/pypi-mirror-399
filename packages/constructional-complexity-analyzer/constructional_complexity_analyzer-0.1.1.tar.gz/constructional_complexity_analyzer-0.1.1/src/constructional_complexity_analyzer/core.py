###################################
##	Install and import modules 
###################################

import os
import pandas as pd
import csv
import numpy as np
import math
import importlib.resources as resources
from .utils import (
    type_token_ratio,
    moving_window_ttr,
    measure_of_textual_lexical_diversity_original,
    measure_of_textual_lexical_diversity_bidirectional,
    measure_of_textual_lexical_diversity_ma_wrap,
    Hypergeometric_distribution_diversity,
)

from collections import defaultdict
import more_itertools
from collections import Counter
from scipy.stats import hypergeom

import torch
from torch.cuda.amp import autocast

import spacy
nlp = spacy.load("en_core_web_sm") # Load parser



##############################################
## GPU setup
##############################################

import torch

if torch.cuda.is_available():

    # Tell PyTorch to use the GPU
    device = torch.device("cuda")
    print('There are %d GPU(s) available.' % torch.cuda.device_count())
    print('We will use the GPU:', torch.cuda.get_device_name(0))

else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")


# Load the fine-tuned construction classification model

import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification
from huggingface_hub import hf_hub_download

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Initialize architecture
model = RobertaForSequenceClassification.from_pretrained("roberta-base", num_labels=10)
tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

# Download weights from Hugging Face Hub (or other host)
model_path = hf_hub_download(
    repo_id="Haerim/roberta_20250415_170332_model",
    filename="roberta_20250415_170332_model.pt"
)

# Load the fine-tuned weights safely from package resources
# with resources.as_file(
#     resources.files("constructional_complexity_analyzer.models") / "roberta_20250415_170332_model.pt"
# ) as model_path:
#     state_dict = torch.load(model_path, map_location=device)
#     model.load_state_dict(state_dict)

state_dict = torch.load(model_path, map_location=device)
model.load_state_dict(state_dict)
model = model.to(device)



##############################################
## Extract verb and dependency information
##############################################

# Prepare CSV file

def extract_verb_dependency_info(input_path,
                                 csv_path="CSV_verb_dependency_information.csv",
                                 xlsx_path="XLSX_verb_dependency_information.xlsx"):
    """
    Extract verb dependency information from all text files in a directory,
    save results to CSV/XLSX, and return a DataFrame.

    Parameters:
        input_path (str): Path to the folder containing text files
        csv_path (str): Path to save the CSV output
        xlsx_path (str): Path to save the XLSX output

    Returns:
        pd.DataFrame: DataFrame containing verb dependency information.
    """
    rows = []

    # Collect all .txt files from the input directory
    file_list = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".txt")]

    with open(csv_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["file_name", "sentence_raw", "verb", "dependency", "dependent_list", "dependent_count"])

        for file_name in file_list:
            with open(file_name, "r", encoding="utf-8-sig") as f:
                text = f.read()
            print(f"Processing {file_name} =====================================")

            doc = nlp(text)
            for sent in doc.sents:
                sent_doc = nlp(sent.text)
                for token in sent_doc:
                    if (token.pos_ == "VERB" and token.dep_ != "aux") or (token.pos_ == "AUX" and token.dep_ != "aux"):
                        dependent_list = [child.dep_ for child in token.children]
                        dep_string = " ".join(dependent_list)
                        dependent_count = len(dependent_list)

                        row = [os.path.basename(file_name), sent.text, token.lemma_, dep_string, dependent_list, dependent_count]
                        writer.writerow(row)
                        rows.append(row)

    # Convert CSV to XLSX
    df = pd.read_csv(csv_path)
    df.to_excel(xlsx_path, index=False)
    print(f"Saved results to {xlsx_path}")
    return df



############################################################
##	Construction identification
############################################################

def construction_identification(input_path,  # 👈 directory containing raw text files
                                csv_path="CSV_verb_dependency_information.csv",
                                xlsx_path="XLSX_verb_dependency_information.xlsx",
                                output_csv="CSV_construction_identification.csv"):
    """
    Run verb dependency extraction + construction identification in one pipeline.

    Parameters:
        input_path (str): Path to folder containing raw text files
        csv_path (str): Path to save intermediate verb dependency CSV.
        xlsx_path (str): Path to save intermediate verb dependency XLSX
        output_csv (str): Path to save construction identification results

    Returns:
        pd.DataFrame: DataFrame of construction identification results.
    """

    # Step 1: Extract verb dependency info from raw text files
    df_verb_dependency_info = extract_verb_dependency_info(
        input_path=input_path,
        csv_path=csv_path,
        xlsx_path=xlsx_path
    )

    # Step 2: Construction identification
    id_to_label = {
        0: 'attributive',
        1: 'caused_motion',
        2: 'ditransitive',
        3: 'existential',
        4: 'intransitive_motion',
        5: 'intransitive_resultative',
        6: 'passive',
        7: 'simple_intransitive',
        8: 'simple_transitive',
        9: 'transitive_resultative'
    }

    results = []

    # Write header once
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['file_name', 'verb', 'dependency', 'dependent_count', 'sentence_raw', 'predicted_label'])
        writer.writeheader()

    for idx, row in df_verb_dependency_info.iterrows():
        source = row.get('file_name', idx)  
        verb = row['verb']
        dependency = row['dependency']
        dependent_count = row['dependent_count']
        sentence = row['sentence_raw']

        combined = f"{dependency} [SEP] {verb} [SEP] {sentence}"
        encoding = tokenizer(combined, return_tensors='pt', truncation=True, padding=True, max_length=512)
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)

        with torch.no_grad():
            with autocast():
                result = model(input_ids, attention_mask=attention_mask)

        predicted_id = torch.argmax(result.logits, dim=1).item()
        predicted_label = id_to_label[predicted_id]

        print(idx + 1, source, verb, dependency, dependent_count, sentence, predicted_label)

        result_row = {
            'file_name': source,
            'verb': verb,
            'dependency': dependency,
            'dependent_count': dependent_count,
            'sentence_raw': sentence,
            'predicted_label': predicted_label
        }
        results.append(result_row)

        with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=result_row.keys())
            writer.writerow(result_row)



############################################################
## Create a construction list and a verb list for each text
############################################################

def create_construction_and_verb_lists(csv_path="CSV_construction_identification.csv"):
    """
    Create a construction list and a verb list for each text from a CSV file.

    Parameters:
        csv_path (str): Path to the CSV file containing construction identification results.

    Returns:
        tuple: (construction_list, verb_list) as dictionaries
    """
    construction_list = defaultdict(list)
    verb_list = defaultdict(list)

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            source = row["file_name"]  
            predicted_label = row["predicted_label"]
            verb = row["verb"]

            construction_list[source].append(predicted_label)
            verb_list[source].append(verb)

    # Convert defaultdicts to regular dicts
    construction_list = dict(construction_list)
    verb_list = dict(verb_list)

    print("Construction list:", construction_list)
    print("Verb list:", verb_list)

    return construction_list, verb_list



############################################################
## Constructional diversity and elaboration indices
############################################################

def compute_constructional_metrics(csv_path="CSV_construction_identification.csv"):
    """
    Compute constructional diversity and elaboration metrics from a CSV file.

    Parameters:
        csv_path (str): Path to the CSV file containing construction identification results.

    Returns:
        tuple: (results_df, dependent_counter)
            results_df (pd.DataFrame): DataFrame of constructional diversity metrics.
            dependent_counter (dict): Dictionary for dependent counter (constructional elaboration).
    """

    construction_list, verb_list = create_construction_and_verb_lists(csv_path)

    results_constructional_diversity = []
    seen_sources = set()
    dependent_counter = defaultdict(lambda: {"total": 0, "count": 0})

    with open(csv_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            source = row['file_name']
            construction = row['predicted_label']
            key = (source, construction)  # elaboration per construction per file

            # Constructional elaboration
            try:
                count = int(float(row["dependent_count"]))
                dependent_counter[key]["total"] += count
                dependent_counter[key]["count"] += 1

            except (KeyError, ValueError, TypeError):
                # skip if missing or invalid
                dependent_counter[key]["total"] = 0
                dependent_counter[key]["count"] = 0

            # Constructional diversity
            if source in seen_sources:
                continue  # skip duplicate sources
            seen_sources.add(source)

            token_frequency = len(construction_list.get(source, []))
            type_frequency = len(set(construction_list.get(source, [])))
            log_transformed_type_frequency = np.log10(type_frequency + 1)

            ttr = 0.0 if token_frequency == 0 else type_frequency / token_frequency
            rttr = 0.0 if token_frequency == 0 else type_frequency / math.sqrt(token_frequency)
            herdan = 0.0 if token_frequency == 0 else np.log(type_frequency) / np.log(token_frequency)

            maas = 0.0 if token_frequency == 0 else (
                (np.log(token_frequency) - np.log(type_frequency)) / (np.log(token_frequency) ** 2)
            )
            mattr = moving_window_ttr(construction_list[source])
            hdd = Hypergeometric_distribution_diversity(construction_list[source])

            mtld_original = measure_of_textual_lexical_diversity_original(construction_list[source])
            mtld_ma_bi = measure_of_textual_lexical_diversity_bidirectional(construction_list[source])
            mtld_ma_wrap = measure_of_textual_lexical_diversity_ma_wrap(construction_list[source])

            results_constructional_diversity.append({
                "File_Name": source,
                "Token_Frequency": token_frequency,
                "Type_Frequency": type_frequency,
                "Log_Transformed_Type_Frequency": round(log_transformed_type_frequency, 4),
                "TTR": round(ttr, 4),
                "RTTR": round(rttr, 4),
                "Herdan": round(herdan, 4),
                "Maas": round(maas, 4),
                "MATTR": mattr if isinstance(mattr, str) else round(mattr, 4),
                "HDD": hdd if isinstance(hdd, str) else round(hdd, 4),
                "MTLD_Original": mtld_original if isinstance(mtld_original, str) else round(mtld_original, 4),
                "MTLD_MA_BI": mtld_ma_bi if isinstance(mtld_ma_bi, str) else round(mtld_ma_bi, 4),
                "MTLD_MA_WRAP": mtld_ma_wrap if isinstance(mtld_ma_wrap, str) else round(mtld_ma_wrap, 4),
            })

    results_df = pd.DataFrame(results_constructional_diversity)
    return results_df, dependent_counter



############################################################
## Save output
############################################################

def save_constructional_outputs(identification_csv="CSV_construction_identification.csv",
                                diversity_out="CSV_constructional_diversity_output.csv",
                                elaboration_out="CSV_constructional_elaboration_output.csv",
                                verb_out="CSV_verb_inventory_size_output.csv",
                                construction_out="CSV_construction_frequency_proportion_output.csv"):
    """
    Save constructional diversity, elaboration, and verb inventory size outputs to CSV files.

    Returns:
        tuple: (df_diversity, df_elaboration, df_verb)
            df_diversity (pd.DataFrame): Constructional diversity results.
            df_elaboration (pd.DataFrame): Constructional elaboration results (wide format).
            df_verb (pd.DataFrame): Verb inventory size indices.
            df_construction (pd.DataFrame): Construction frequency / proportion indices.
    """

    # --- Compute diversity + elaboration ---
    results_constructional_diversity, dependent_counter = compute_constructional_metrics(
        csv_path=identification_csv
    )

    # --- Save constructional diversity ---
    results_constructional_diversity.to_csv(diversity_out, index=False)
    print(f"Saved constructional diversity to {diversity_out}")

    # --- Build elaboration rows ---
    elaboration_rows = []
    for (file_name, construction), stats in dependent_counter.items():
        avg = stats["total"] / stats["count"] if stats["count"] > 0 else 0
        elaboration_rows.append({
            "file_name": file_name,
            "construction": construction,
            "constructional_elaboration": avg
        })

    df_elaboration_long = pd.DataFrame(elaboration_rows)

    # --- Pivot to wide format: one row per file, one column per construction ---
    df_elaboration = df_elaboration_long.pivot_table(
        index="file_name",
        columns="construction",
        values="constructional_elaboration",
        fill_value=0
    ).reset_index()

    # Round and rename columns
    df_elaboration.iloc[:, 1:] = df_elaboration.iloc[:, 1:].round(4)
    df_elaboration.rename(
        columns={col: f"constructional_elaboration_{col}" for col in df_elaboration.columns if col != "file_name"},
        inplace=True
    )

    df_elaboration.to_csv(elaboration_out, index=False)
    print(f"Saved constructional elaboration indices to {elaboration_out}")

    # --- Compute verb inventory size indices ---
    df = pd.read_csv(identification_csv)
    unique_verb_counts = (
        df.groupby(['file_name', 'predicted_label'])['verb']
        .nunique()
        .reset_index(name='unique_verb_count')
    )
    unique_verb_counts['log_unique_verb_count'] = np.log10(unique_verb_counts['unique_verb_count'] + 1)

    pivot_table = unique_verb_counts.pivot_table(
        index='file_name',
        columns='predicted_label',
        values='log_unique_verb_count',
        fill_value=0
    ).reset_index()

    pivot_table.iloc[:, 1:] = pivot_table.iloc[:, 1:].round(4)
    pivot_table.rename(
        columns={col: f"verb_inventory_size_{col}" for col in pivot_table.columns if col != 'file_name'},
        inplace=True
    )

    pivot_table.to_csv(verb_out, index=False)
    print(f"Saved verb inventory size indices to {verb_out}")


    # --- Compute verb inventory size indices ---
    counts = (
        df.groupby(["file_name", "predicted_label"])
        .size()
        .reset_index(name="count")
    )

    counts_wide = counts.pivot_table(
        index="file_name",
        columns="predicted_label",
        values="count",
        fill_value=0
    )

    counts_wide["total"] = counts_wide.sum(axis=1)

    proportions_wide = counts_wide.div(counts_wide["total"], axis=0)

    merged = pd.concat(
        {"frequency": counts_wide, "proportion": proportions_wide},
        axis=1
    )

    merged.to_csv(construction_out, index=False)
    print(f"Saved construction count/proportion indices to {construction_out}")

    return results_constructional_diversity, df_elaboration, pivot_table, merged



############################################################
## Run all
############################################################

import os
import pandas as pd

def run_constructional_analysis(
    input_text_dir,
    diversity_out="CSV_constructional_diversity_output.csv",
    elaboration_out="CSV_constructional_elaboration.csv",
    verb_out="CSV_verb_inventory_size_output.csv",
    construction_out="CSV_construction_frequency_proportion_output.csv"
):
    """
    Full pipeline: extract verb dependencies, identify constructions,
    compute metrics, and save outputs in the same directory as input_text_dir.
    """

    # Ensure outputs are saved inside the input directory
    diversity_out = os.path.join(input_text_dir, diversity_out)
    elaboration_out = os.path.join(input_text_dir, elaboration_out)
    verb_out = os.path.join(input_text_dir, verb_out)
    construction_out = os.path.join(input_text_dir, construction_out)

    # Step 1: Extract verb dependency info
    extract_verb_dependency_info(
        input_path=input_text_dir,
        csv_path=os.path.join(input_text_dir, "CSV_verb_dependency_information.csv"),
        xlsx_path=os.path.join(input_text_dir, "XLSX_verb_dependency_information.xlsx"),
    )

    # Step 2: Run construction identification
    construction_identification(
        input_text_dir,
        csv_path=os.path.join(input_text_dir, "CSV_verb_dependency_information.csv"),
        xlsx_path=os.path.join(input_text_dir, "XLSX_verb_dependency_information.xlsx"),
        output_csv=os.path.join(input_text_dir, "CSV_construction_identification.csv"),
    )

    # Step 3: Compute metrics + save outputs
    df_diversity, df_elaboration, df_verb, df_construction = save_constructional_outputs(
        identification_csv=os.path.join(input_text_dir, "CSV_construction_identification.csv"),
        diversity_out=diversity_out,
        elaboration_out=elaboration_out,
        verb_out=verb_out,
        construction_out=construction_out,
    )

    # Step 4: Clean up intermediate files
    for file_name in ["CSV_verb_dependency_information.csv",
                      "XLSX_verb_dependency_information.xlsx"]:
        file_path = os.path.join(input_text_dir, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")

    return df_diversity, df_elaboration, df_verb, df_construction
