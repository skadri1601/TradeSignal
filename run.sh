#!/usr/bin/env bash
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

print_banner() {
    echo -e "${CYAN}"
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║         TradeSignal Launcher          ║"
    echo "  ╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

check_command() {
    if ! command -v "$1" &>/dev/null; then
        echo -e "${RED}Error: '$1' is not installed or not in PATH.${NC}"
        return 1
    fi
}

detect_os() {
    case "$(uname -s)" in
        Linux*)   OS="linux" ;;
        Darwin*)  OS="mac" ;;
        MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
        *)        OS="unknown" ;;
    esac
    echo -e "${CYAN}Detected OS: ${OS}${NC}"
}

check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    local missing=0

    check_command docker || missing=1
    check_command node   || missing=1
    check_command npm    || missing=1
    check_command python3 2>/dev/null || check_command python 2>/dev/null || { echo -e "${RED}Error: python is not installed.${NC}"; missing=1; }

    if ! docker info &>/dev/null 2>&1; then
        echo -e "${RED}Error: Docker daemon is not running. Please start Docker Desktop.${NC}"
        missing=1
    fi

    if [ "$missing" -eq 1 ]; then
        echo -e "${RED}Please install missing dependencies and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}All prerequisites found.${NC}"
}

PYTHON_CMD=""
find_python() {
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
    fi
}

start_docker_services() {
    echo -e "${YELLOW}Starting Docker services (Postgres, Redis)...${NC}"
    cd "$PROJECT_ROOT"
    docker compose up -d postgres redis
    echo -e "${GREEN}Docker services started.${NC}"
}

wait_for_postgres() {
    echo -e "${YELLOW}Waiting for Postgres to be ready...${NC}"
    local retries=30
    while [ $retries -gt 0 ]; do
        if docker exec tradesignal-db pg_isready -U tradesignal &>/dev/null; then
            echo -e "${GREEN}Postgres is ready.${NC}"
            return 0
        fi
        retries=$((retries - 1))
        sleep 1
    done
    echo -e "${RED}Postgres did not become ready in time.${NC}"
    exit 1
}

wait_for_redis() {
    echo -e "${YELLOW}Waiting for Redis to be ready...${NC}"
    local retries=15
    while [ $retries -gt 0 ]; do
        if docker exec tradesignal-redis redis-cli ping 2>/dev/null | grep -q PONG; then
            echo -e "${GREEN}Redis is ready.${NC}"
            return 0
        fi
        retries=$((retries - 1))
        sleep 1
    done
    echo -e "${RED}Redis did not become ready in time.${NC}"
    exit 1
}

setup_backend() {
    echo -e "${YELLOW}Setting up backend...${NC}"
    cd "$PROJECT_ROOT/backend"

    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        echo -e "${CYAN}Creating Python virtual environment...${NC}"
        $PYTHON_CMD -m venv venv
    fi

    if [ -d "venv" ]; then
        VENV_DIR="venv"
    else
        VENV_DIR=".venv"
    fi

    if [ "$OS" = "windows" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi

    pip install -q -r requirements.txt
    echo -e "${GREEN}Backend dependencies installed.${NC}"
}

setup_frontend() {
    echo -e "${YELLOW}Setting up frontend...${NC}"
    cd "$PROJECT_ROOT/frontend"

    if [ ! -d "node_modules" ]; then
        echo -e "${CYAN}Installing frontend dependencies...${NC}"
        npm install
    fi
    echo -e "${GREEN}Frontend dependencies ready.${NC}"
}

start_backend() {
    echo -e "${YELLOW}Starting backend server...${NC}"
    cd "$PROJECT_ROOT/backend"

    if [ -d "venv" ]; then
        VENV_DIR="venv"
    else
        VENV_DIR=".venv"
    fi

    if [ "$OS" = "windows" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi

    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"
}

start_frontend() {
    echo -e "${YELLOW}Starting frontend dev server...${NC}"
    cd "$PROJECT_ROOT/frontend"
    npm run dev &
    FRONTEND_PID=$!
    echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"
}

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
    echo -e "${CYAN}Stop Docker services too? (y/N): ${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        cd "$PROJECT_ROOT"
        docker compose down
        echo -e "${GREEN}Docker services stopped.${NC}"
    fi
    echo -e "${GREEN}Goodbye!${NC}"
    exit 0
}

show_help() {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       Start everything (default)"
    echo "  docker      Start only Docker services"
    echo "  backend     Start only the backend"
    echo "  frontend    Start only the frontend"
    echo "  stop        Stop Docker services"
    echo "  help        Show this help"
}

cmd_docker() {
    start_docker_services
    wait_for_postgres
    wait_for_redis
}

cmd_backend() {
    find_python
    setup_backend
    start_backend
}

cmd_frontend() {
    setup_frontend
    start_frontend
}

cmd_start() {
    cmd_docker
    find_python
    setup_backend
    setup_frontend
    start_backend
    start_frontend

    echo ""
    echo -e "${GREEN}══════════════════════════════════════${NC}"
    echo -e "${GREEN}  TradeSignal is running!${NC}"
    echo -e "${GREEN}  Frontend: http://localhost:5174${NC}"
    echo -e "${GREEN}  Backend:  http://localhost:8000${NC}"
    echo -e "${GREEN}  API Docs: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}══════════════════════════════════════${NC}"
    echo -e "${CYAN}  Press Ctrl+C to stop${NC}"
    echo ""

    trap cleanup SIGINT SIGTERM
    wait
}

cmd_stop() {
    cd "$PROJECT_ROOT"
    echo -e "${YELLOW}Stopping Docker services...${NC}"
    docker compose down
    echo -e "${GREEN}Done.${NC}"
}

print_banner
detect_os
check_prerequisites

case "${1:-start}" in
    start)    cmd_start ;;
    docker)   cmd_docker ;;
    backend)  cmd_backend; trap cleanup SIGINT SIGTERM; wait ;;
    frontend) cmd_frontend; trap cleanup SIGINT SIGTERM; wait ;;
    stop)     cmd_stop ;;
    help|-h|--help) show_help ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
