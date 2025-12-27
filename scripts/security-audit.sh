#!/bin/bash

# VEETSSUITES Security Audit Script
# This script performs comprehensive security checks on the codebase

set -e

echo "🔒 Starting VEETSSUITES Security Audit..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the project root
if [ ! -f "README.md" ] || [ ! -d "frontend" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

echo "1. Checking for hardcoded secrets..."
echo "-----------------------------------"

# Check for common secret patterns
SECRET_PATTERNS=(
    "password\s*=\s*['\"][^'\"]*['\"]"
    "secret\s*=\s*['\"][^'\"]*['\"]"
    "api_key\s*=\s*['\"][^'\"]*['\"]"
    "token\s*=\s*['\"][^'\"]*['\"]"
    "sk_live_"
    "pk_live_"
    "rk_live_"
    "AKIA[0-9A-Z]{16}"
    "-----BEGIN PRIVATE KEY-----"
    "-----BEGIN RSA PRIVATE KEY-----"
)

SECRETS_FOUND=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -E "$pattern" --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude="*.log" . > /dev/null 2>&1; then
        print_warning "Potential secret found matching pattern: $pattern"
        grep -r -E "$pattern" --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude="*.log" . | head -5
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    fi
done

if [ $SECRETS_FOUND -eq 0 ]; then
    print_status "No hardcoded secrets detected"
else
    print_error "$SECRETS_FOUND potential secret patterns found"
fi

echo ""
echo "2. Checking environment variable usage..."
echo "----------------------------------------"

# Check that sensitive values use environment variables
ENV_CHECKS=0
if grep -r "process\.env\." frontend/lib/ frontend/components/ > /dev/null 2>&1; then
    print_status "Frontend uses environment variables"
else
    print_warning "Frontend may not be using environment variables properly"
    ENV_CHECKS=$((ENV_CHECKS + 1))
fi

if grep -r "os\.environ\|getenv" backend/ > /dev/null 2>&1; then
    print_status "Backend uses environment variables"
else
    print_warning "Backend may not be using environment variables properly"
    ENV_CHECKS=$((ENV_CHECKS + 1))
fi

echo ""
echo "3. Frontend dependency audit..."
echo "------------------------------"

cd frontend
if command -v npm > /dev/null 2>&1; then
    if npm audit --audit-level=moderate > /dev/null 2>&1; then
        print_status "No moderate or high severity vulnerabilities in frontend dependencies"
    else
        print_warning "Frontend dependencies have security vulnerabilities"
        npm audit --audit-level=moderate
    fi
else
    print_error "npm not found, skipping frontend audit"
fi
cd ..

echo ""
echo "4. Backend dependency audit..."
echo "-----------------------------"

cd backend
if command -v pip > /dev/null 2>&1; then
    if command -v safety > /dev/null 2>&1; then
        if safety check -r requirements.txt > /dev/null 2>&1; then
            print_status "No known security vulnerabilities in backend dependencies"
        else
            print_warning "Backend dependencies have security vulnerabilities"
            safety check -r requirements.txt
        fi
    else
        print_warning "Safety not installed, install with: pip install safety"
    fi
else
    print_error "pip not found, skipping backend audit"
fi
cd ..

echo ""
echo "5. Checking file permissions..."
echo "------------------------------"

# Check for overly permissive files
PERM_ISSUES=0
if find . -type f -perm 777 2>/dev/null | grep -v node_modules | grep -v venv | grep -v .git > /dev/null; then
    print_warning "Files with 777 permissions found:"
    find . -type f -perm 777 2>/dev/null | grep -v node_modules | grep -v venv | grep -v .git
    PERM_ISSUES=$((PERM_ISSUES + 1))
else
    print_status "No overly permissive files found"
fi

echo ""
echo "6. Checking for debug code..."
echo "----------------------------"

DEBUG_PATTERNS=(
    "console\.log"
    "console\.debug"
    "print("
    "pdb\.set_trace"
    "debugger;"
    "TODO.*security"
    "FIXME.*security"
)

DEBUG_FOUND=0
for pattern in "${DEBUG_PATTERNS[@]}"; do
    if grep -r -E "$pattern" --exclude-dir=node_modules --exclude-dir=venv --exclude-dir=.git --exclude="*.log" --exclude-dir=__tests__ --exclude-dir=tests . > /dev/null 2>&1; then
        print_warning "Debug code found matching pattern: $pattern"
        DEBUG_FOUND=$((DEBUG_FOUND + 1))
    fi
done

if [ $DEBUG_FOUND -eq 0 ]; then
    print_status "No debug code patterns detected"
else
    print_warning "$DEBUG_FOUND debug code patterns found (review for production readiness)"
fi

echo ""
echo "7. Checking configuration files..."
echo "---------------------------------"

# Check for secure configuration
CONFIG_ISSUES=0

# Check Django settings
if [ -f "backend/veetssuites/settings.py" ]; then
    if grep -q "DEBUG = True" backend/veetssuites/settings.py; then
        print_warning "Django DEBUG is set to True (should be False in production)"
        CONFIG_ISSUES=$((CONFIG_ISSUES + 1))
    else
        print_status "Django DEBUG configuration looks good"
    fi
    
    if grep -q "ALLOWED_HOSTS = \[\]" backend/veetssuites/settings.py; then
        print_warning "Django ALLOWED_HOSTS is empty (configure for production)"
        CONFIG_ISSUES=$((CONFIG_ISSUES + 1))
    else
        print_status "Django ALLOWED_HOSTS is configured"
    fi
fi

# Check Next.js configuration
if [ -f "frontend/next.config.js" ]; then
    if grep -q "experimental" frontend/next.config.js; then
        print_warning "Next.js experimental features detected (review for production stability)"
    else
        print_status "Next.js configuration looks stable"
    fi
fi

echo ""
echo "8. Checking HTTPS and security headers..."
echo "----------------------------------------"

# Check for security middleware
if grep -r "SecurityMiddleware\|SECURE_SSL_REDIRECT\|SECURE_HSTS" backend/ > /dev/null 2>&1; then
    print_status "Django security middleware detected"
else
    print_warning "Django security middleware may not be configured"
    CONFIG_ISSUES=$((CONFIG_ISSUES + 1))
fi

# Check for CORS configuration
if grep -r "CORS_ALLOWED_ORIGINS\|CORS_ALLOW_ALL_ORIGINS" backend/ > /dev/null 2>&1; then
    print_status "CORS configuration detected"
else
    print_warning "CORS configuration may not be set"
    CONFIG_ISSUES=$((CONFIG_ISSUES + 1))
fi

echo ""
echo "9. Checking authentication security..."
echo "-------------------------------------"

# Check for JWT configuration
if grep -r "JWT_AUTH\|SIMPLE_JWT" backend/ > /dev/null 2>&1; then
    print_status "JWT authentication configuration found"
else
    print_warning "JWT authentication may not be configured"
fi

# Check for password validation
if grep -r "AUTH_PASSWORD_VALIDATORS" backend/ > /dev/null 2>&1; then
    print_status "Password validation configured"
else
    print_warning "Password validation may not be configured"
fi

echo ""
echo "10. Final security recommendations..."
echo "-----------------------------------"

print_status "Security audit completed!"
echo ""

TOTAL_ISSUES=$((SECRETS_FOUND + ENV_CHECKS + PERM_ISSUES + CONFIG_ISSUES))

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}🎉 No critical security issues found!${NC}"
    echo ""
    echo "Recommendations for production:"
    echo "• Ensure all environment variables are properly set"
    echo "• Enable HTTPS and security headers"
    echo "• Set up monitoring and logging"
    echo "• Regular dependency updates"
    echo "• Implement rate limiting"
    echo "• Set up backup and disaster recovery"
else
    echo -e "${YELLOW}⚠ $TOTAL_ISSUES potential security issues found${NC}"
    echo ""
    echo "Please review and address the warnings above before production deployment."
fi

echo ""
echo "Additional security tools to consider:"
echo "• Snyk (https://snyk.io/) for continuous monitoring"
echo "• OWASP ZAP for penetration testing"
echo "• Bandit for Python security linting"
echo "• ESLint security plugin for JavaScript"
echo ""

exit $TOTAL_ISSUES