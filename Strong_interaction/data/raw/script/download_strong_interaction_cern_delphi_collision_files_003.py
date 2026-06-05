#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_cern_delphi_collision_files_003.py

Controlled downloader for batch-03 DELPHI collision-data file candidates.

Author: Kwon Dominicus

Purpose
-------
The batch-03 record/file parser identified DELPHI collision-data file candidates,
mostly in CERN EOS public paths such as:

    root://eospublic.cern.ch//eos/opendata/delphi/collision-data/...

This script performs controlled, limited downloads from:

    Strong_interaction/data/raw/references/03/
        strong_interaction_cern_delphi_record_file_candidates_collision_shortlist_raw_003.csv

Outputs:
    Strong_interaction/data/raw/source_tables/03/collision_file_downloads/
    Strong_interaction/data/raw/references/03/
        strong_interaction_cern_delphi_collision_file_download_manifest_raw_003.csv
        strong_interaction_cern_delphi_collision_file_download_summary_raw_003.txt

Important
---------
Do not