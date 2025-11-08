#!/bin/bash
# Script to push to GitHub using Personal Access Token

echo "🚀 Pushing to GitHub..."
echo ""
echo "This script will help you push your changes to GitHub."
echo "You'll need a Personal Access Token from GitHub."
echo ""
echo "To create a token:"
echo "1. Go to: https://github.com/settings/tokens"
echo "2. Click 'Generate new token' → 'Generate new token (classic)'"
echo "3. Name it: 'HackPrinceton-2025'"
echo "4. Select scope: 'repo'"
echo "5. Click 'Generate token'"
echo "6. Copy the token"
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
echo "📤 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "🔒 For security, consider removing the token from the URL:"
    echo "   git remote set-url origin https://github.com/celloii/HackPrinceton-2025.git"
else
    echo ""
    echo "❌ Push failed. Please check your token and try again."
fi

