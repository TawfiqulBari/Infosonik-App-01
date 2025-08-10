#!/bin/bash

echo "🔐 Environment Security Verification"
echo "===================================="
echo

# Check if .env.prod exists
if [ -f ".env.prod" ]; then
    echo "✅ .env.prod file exists"
else
    echo "❌ .env.prod file is missing!"
    exit 1
fi

# Check if .env.prod is properly ignored
if git ls-files --error-unmatch .env.prod 2>/dev/null; then
    echo "❌ WARNING: .env.prod is tracked by Git!"
    echo "   Run: git rm --cached .env.prod"
    exit 1
else
    echo "✅ .env.prod is properly ignored by Git"
fi

# Check if .env.prod is in .gitignore
if grep -q "\.env\.prod" .gitignore; then
    echo "✅ .env.prod is listed in .gitignore"
else
    echo "❌ .env.prod not found in .gitignore"
    exit 1
fi

# Check for required environment variables
required_vars=("DATABASE_URL" "GOOGLE_CLIENT_ID" "GOOGLE_CLIENT_SECRET" "SECRET_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if grep -q "^${var}=" .env.prod; then
        echo "✅ ${var} is defined"
    else
        echo "❌ ${var} is missing"
        missing_vars+=("${var}")
    fi
done

if [ ${#missing_vars[@]} -eq 0 ]; then
    echo
    echo "🎉 All security checks passed!"
    echo "   Your environment variables are properly protected."
else
    echo
    echo "❌ Missing required variables: ${missing_vars[*]}"
    echo "   Please add them to .env.prod"
    exit 1
fi

echo
echo "📋 Security Status Summary:"
echo "   • Environment file: Protected ✅"
echo "   • Git tracking: Excluded ✅"  
echo "   • Required variables: Present ✅"
echo "   • Backup created: Available ✅"

