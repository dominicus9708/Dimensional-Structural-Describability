#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_cern_delphi_collision_files_003.py

Controlled downloader for batch-03 DELPHI collision-data file candidates.

Author: Kwon Dominicus

Purpose
-------
The batch-03 record/file parser identified DELPHI collision-data files with
root:// EOS public URLs, including .al/.xsdst/.fadana candidates. This script
performs controlled downloads from:

    Strong_interaction/data/raw/references/03/
        strong_interaction_cern_delphi_record_file