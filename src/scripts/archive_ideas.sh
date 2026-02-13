#!/bin/bash
# Archive processed ideas

mkdir -p ideas/archived
mv ideas/*.md ideas/archived/ 2>/dev/null
echo "Archived all processed ideas."
