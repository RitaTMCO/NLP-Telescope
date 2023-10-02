#!/bin/sh

python split_ref_id_terms.py -i test-WinoMT/pt_ref_google_id_terms.txt -t test-WinoMT/pt_id_terms_google.txt -r test-WinoMT/pt_ref_google.txt
python split_ref_id_terms.py -i test-WinoMT-Pro/pt_pro_ref_google_id_terms.txt -t test-WinoMT-Pro/pt_pro_id_terms_google.txt -r test-WinoMT-Pro/pt_pro_ref_google.txt
python split_ref_id_terms.py -i test-WinoMT-Anti/pt_anti_ref_google_id_terms.txt -t test-WinoMT-Anti/pt_anti_id_terms_google.txt -r test-WinoMT-Anti/pt_anti_ref_google.txt

python split_ref_id_terms.py -i test-WinoMT/pt_ref_microsoft_id_terms.txt -t test-WinoMT/pt_id_terms_microsoft.txt -r test-WinoMT/pt_ref_microsoft.txt
python split_ref_id_terms.py -i test-WinoMT-Pro/pt_pro_ref_microsoft_id_terms.txt -t test-WinoMT-Pro/pt_pro_id_terms_microsoft.txt -r test-WinoMT-Pro/pt_pro_ref_microsoft.txt
python split_ref_id_terms.py -i test-WinoMT-Anti/pt_anti_ref_microsoft_id_terms.txt -t test-WinoMT-Anti/pt_anti_id_terms_microsoft.txt -r test-WinoMT-Anti/pt_anti_ref_microsoft.txt