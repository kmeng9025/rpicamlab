#!/bin/bash
lxterminal --working-directory="$(pwd)" -e "bash -c './startCentralPi.sh; exec bash'"
