#!/bin/bash
cd /home/kavia/workspace/code-generation/simplenotes-163666-163806/SimpleNotesApplicationContainer
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

