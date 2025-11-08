#!/bin/bash
# Script to sync with GitHub (pull remote changes, then push)

echo "🔄 Syncing with GitHub..."
echo ""
echo "This script will:"
echo "1. Pull remote changes from GitHub"
echo "2. Merge them with your local changes"
echo "3. Push everything back to GitHub"
echo ""
read -p "Enter your Personal Access Token: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ No token provided. Exiting."
    exit 1
fi

echo ""
echo "📝 Updating remote URL with token..."
git remote set-url origin https://${TOKEN}@github.com/celloii/HackPrinceton-2025.git

echo ""
echo "📥 Pulling remote changes..."
git pull origin main --no-rebase --allow-unrelated-histories

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Pull had conflicts. Attempting to merge..."
    git merge origin/main --allow-unrelated-histories --no-edit
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  There are merge conflicts that need to be resolved manually."
        echo "   Run 'git status' to see which files have conflicts."
        echo "   After resolving conflicts, run 'git add .' and 'git commit'"
        exit 1
    fi
fi

echo ""
echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully synced with GitHub!"
    echo "🔒 For security, consider removing the token from the URL:"
    echo "   git remote set-url origin https://github.com/celloii/HackPrinceton-2025.git"
else
    echo ""
    echo "❌ Push failed. There may be conflicts that need to be resolved."
    echo "   Check the error message above for details."
fi

