#!/bin/bash
# Deployment Verification Script
# Verifies that all services are running correctly after deployment

set -e

echo "🔍 Starting deployment verification..."

# Configuration
API_URL="${API_URL:-http://localhost:5000}"
TIMEOUT=30
MAX_RETRIES=5

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to check if service is responding
check_service() {
    local url=$1
    local service_name=$2
    local retry_count=0
    
    echo "Checking $service_name..."
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if curl -f -s --max-time $TIMEOUT "$url" > /dev/null 2>&1; then
            print_success "$service_name is responding"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            echo "  Retry $retry_count/$MAX_RETRIES..."
            sleep 5
        fi
    done
    
    print_error "$service_name is not responding after $MAX_RETRIES attempts"
    return 1
}

# Function to check API endpoint
check_api_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo "Testing $description..."
    
    response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint" 2>/dev/null || echo "000")
    status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "$expected_status" ]; then
        print_success "$description returned status $status_code"
        return 0
    else
        print_error "$description returned status $status_code (expected $expected_status)"
        return 1
    fi
}

# Function to check database connection
check_database() {
    echo "Checking database connection..."
    
    if docker-compose exec -T postgres_primary pg_isready > /dev/null 2>&1; then
        print_success "PostgreSQL primary is ready"
    else
        print_error "PostgreSQL primary is not ready"
        return 1
    fi
    
    # Check replica if exists
    if docker-compose ps | grep -q postgres_replica1; then
        if docker-compose exec -T postgres_replica1 pg_isready > /dev/null 2>&1; then
            print_success "PostgreSQL replica is ready"
        else
            print_warning "PostgreSQL replica is not ready"
        fi
    fi
}

# Function to check Redis
check_redis() {
    echo "Checking Redis connection..."
    
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        print_success "Redis is responding"
        return 0
    else
        print_error "Redis is not responding"
        return 1
    fi
}

# Function to check monitoring services
check_monitoring() {
    echo "Checking monitoring services..."
    
    # Check Prometheus
    if curl -f -s --max-time 10 "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        print_success "Prometheus is healthy"
    else
        print_warning "Prometheus is not accessible"
    fi
    
    # Check Grafana
    if curl -f -s --max-time 10 "http://localhost:3000/api/health" > /dev/null 2>&1; then
        print_success "Grafana is healthy"
    else
        print_warning "Grafana is not accessible"
    fi
}

# Function to check disk space
check_disk_space() {
    echo "Checking disk space..."
    
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -lt 80 ]; then
        print_success "Disk usage is ${disk_usage}% (healthy)"
    elif [ "$disk_usage" -lt 90 ]; then
        print_warning "Disk usage is ${disk_usage}% (getting high)"
    else
        print_error "Disk usage is ${disk_usage}% (critical)"
    fi
}

# Function to check memory usage
check_memory() {
    echo "Checking memory usage..."
    
    if command -v free > /dev/null 2>&1; then
        mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
        
        if [ "$mem_usage" -lt 80 ]; then
            print_success "Memory usage is ${mem_usage}% (healthy)"
        elif [ "$mem_usage" -lt 90 ]; then
            print_warning "Memory usage is ${mem_usage}% (getting high)"
        else
            print_error "Memory usage is ${mem_usage}% (critical)"
        fi
    else
        print_warning "Cannot check memory usage (free command not available)"
    fi
}

# Function to test pipeline processing
test_pipeline() {
    echo "Testing pipeline processing..."
    
    # Create test payload
    test_payload='{
        "input_data": "Photosynthesis is the process by which plants make food.",
        "target_language": "hindi",
        "grade_level": 8,
        "subject": "science",
        "output_format": "text"
    }'
    
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$test_payload" \
        "$API_URL/api/process-content" \
        -w "\n%{http_code}" 2>/dev/null || echo "000")
    
    status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" = "200" ] || [ "$status_code" = "202" ]; then
        print_success "Pipeline processing endpoint is working"
        return 0
    else
        print_warning "Pipeline processing returned status $status_code (may need API key)"
        return 0  # Don't fail verification for this
    fi
}

# Main verification flow
main() {
    echo "========================================="
    echo "  Deployment Verification"
    echo "========================================="
    echo ""
    
    failed_checks=0
    
    # Check core services
    echo "=== Core Services ==="
    check_service "$API_URL/health" "Flask API" || ((failed_checks++))
    check_database || ((failed_checks++))
    check_redis || ((failed_checks++))
    echo ""
    
    # Check API endpoints
    echo "=== API Endpoints ==="
    check_api_endpoint "/health" "200" "Health check endpoint" || ((failed_checks++))
    check_api_endpoint "/metrics" "200" "Metrics endpoint" || ((failed_checks++))
    echo ""
    
    # Test pipeline (optional)
    echo "=== Pipeline Testing ==="
    test_pipeline
    echo ""
    
    # Check monitoring
    echo "=== Monitoring Services ==="
    check_monitoring
    echo ""
    
    # Check system resources
    echo "=== System Resources ==="
    check_disk_space
    check_memory
    echo ""
    
    # Summary
    echo "========================================="
    if [ $failed_checks -eq 0 ]; then
        print_success "All critical checks passed!"
        echo ""
        echo "Access points:"
        echo "  - API: $API_URL"
        echo "  - Prometheus: http://localhost:9090"
        echo "  - Grafana: http://localhost:3000"
        echo ""
        exit 0
    else
        print_error "$failed_checks critical check(s) failed"
        echo ""
        echo "Please review the errors above and check:"
        echo "  - Service logs: docker-compose logs"
        echo "  - Service status: docker-compose ps"
        echo "  - Environment variables: Check .env file"
        echo ""
        exit 1
    fi
}

# Run main function
main
