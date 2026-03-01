if command -v uv &> /dev/null; then
        echo "installing reqs w/ uv"
        uv tool install .
    else
        echo "uv not found - falling back to pip for installation"
        python3 -m pip install -e .
    fi