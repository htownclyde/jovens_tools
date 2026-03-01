if command -v uv &> /dev/null; then
        echo "installing reqs w/ uv"
        uv cache clean
        uv tool install . --force
    else
        echo "uv not found - falling back to pip for installation"
        python3 -m pip install -e .
    fi
jovens_tools