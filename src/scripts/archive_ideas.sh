#!/bin/bash
# Archive processed ideas

mkdir -p specs/ideas/archived
mv specs/ideas/*.md specs/ideas/archived/ 2>/dev/null
echo "Archived all processed ideas."
