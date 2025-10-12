from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import docker
import re

app = FastAPI()

def get_neko_containers():
    """Get all running Neko containers with their ports"""
    client = docker.from_env()
    containers = client.containers.list()
    
    neko_containers = []
    seen_containers = set()
    
    for container in containers:
        # Check if container name or image contains 'neko'
        if 'neko' in container.name.lower() or any('neko' in img.lower() for img in container.image.tags):
            # Skip if already added
            if container.short_id in seen_containers:
                continue
            
            seen_containers.add(container.short_id)
            
            # Get port mappings
            ports = container.attrs['NetworkSettings']['Ports']
            
            # Find the first available port
            for container_port, host_bindings in ports.items():
                if host_bindings:
                    host_port = host_bindings[0]['HostPort']
                    neko_containers.append({
                        'name': container.name,
                        'id': container.short_id,
                        'port': host_port,
                        'url': f'http://localhost:{host_port}'
                    })
                    break  # Only take the first port mapping
    
    return neko_containers

@app.get("/", response_class=HTMLResponse)
async def home():
    containers = get_neko_containers()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Neko Dockers</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #1a1a1a;
                color: #fff;
                padding: 20px;
                overflow-x: hidden;
            }}
            
            h1 {{
                text-align: center;
                margin-bottom: 15px;
                color: #4a9eff;
            }}

            .controls {{
                text-align: center;
                margin-bottom: 30px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 15px;
                color: #aaa;
            }}

            .controls label {{
                display: flex;
                align-items: center;
                gap: 5px;
                cursor: pointer;
            }}

            #countdown {{
                font-weight: 600;
                min-width: 150px;
                text-align: left;
            }}
            
            .grid-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                gap: 20px;
                max-width: 1600px;
                margin: 0 auto;
            }}
            
            .grid-item {{
                background: #2a2a2a;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .grid-item:hover {{
                transform: translateY(-4px);
                box-shadow: 0 8px 12px rgba(74, 158, 255, 0.3);
            }}
            
            .grid-header {{
                padding: 12px 16px;
                background: #333;
                border-bottom: 2px solid #4a9eff;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header-info {{
                flex: 1;
            }}
            
            .kill-btn {{
                background: #ff4757;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                font-weight: 600;
                transition: background 0.2s;
                margin-left: 10px;
            }}
            
            .kill-btn:hover {{
                background: #ff3838;
            }}
            
            .container-name {{
                font-weight: 600;
                font-size: 16px;
                margin-bottom: 4px;
            }}
            
            .container-port {{
                font-size: 14px;
                color: #888;
            }}
            
            .iframe-container {{
                width: 100%;
                height: 300px;
                position: relative;
                overflow: hidden;
            }}
            
            .grid-item iframe {{
                width: 100%;
                height: 100%;
                border: none;
                pointer-events: none;
            }}
            
            .modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }}
            
            .modal.active {{
                display: flex;
            }}
            
            .modal-content {{
                width: 95%;
                height: 95%;
                position: relative;
                background: #1a1a1a;
                border-radius: 8px;
                overflow: hidden;
            }}
            
            .modal-header {{
                padding: 16px 20px;
                background: #2a2a2a;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid #4a9eff;
            }}
            
            .modal-actions {{
                display: flex;
                gap: 10px;
            }}
            
            .kill-btn-modal {{
                background: #ff4757;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: background 0.2s;
            }}
            
            .kill-btn-modal:hover {{
                background: #ff3838;
            }}
            
            .modal-title {{
                font-size: 18px;
                font-weight: 600;
            }}
            
            .close-btn {{
                background: #ff4757;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: background 0.2s;
            }}
            
            .close-btn:hover {{
                background: #ff3838;
            }}
            
            .modal-iframe {{
                width: 100%;
                height: calc(100% - 60px);
                border: none;
            }}
            
            .no-containers {{
                text-align: center;
                padding: 60px 20px;
                color: #888;
                font-size: 18px;
            }}
        </style>
    </head>
    <body>
        <h1>🖥️ Neko Dockers</h1>
        
        <div class="controls">
            <label for="autoRefreshCheckbox">
                <input type="checkbox" id="autoRefreshCheckbox">
                Auto Refresh
            </label>
            <span id="countdown"></span>
        </div>

        <div class="grid-container" id="gridContainer">
            {''.join([f'''
            <div class="grid-item" onclick="openModal('{c['url']}', '{c['name']}', '{c['id']}')">
                <div class="grid-header">
                    <div class="header-info">
                        <div class="container-name">{c['name']}</div>
                        <div class="container-port">Port: {c['port']} | ID: {c['id']}</div>
                    </div>
                    <button class="kill-btn" onclick="event.stopPropagation(); killContainer('{c['id']}')">🗑️ Kill</button>
                </div>
                <div class="iframe-container">
                    <iframe src="{c['url']}" loading="lazy"></iframe>
                </div>
            </div>
            ''' for c in containers]) if containers else '<div class="no-containers">No Neko containers running</div>'}
        </div>
        
        <div class="modal" id="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title" id="modalTitle"></div>
                    <div class="modal-actions">
                        <button class="kill-btn-modal" id="modalKillBtn" onclick="killContainer(null, true)">🗑️ Kill</button>
                        <button class="close-btn" onclick="closeModal()">✕ Close</button>
                    </div>
                </div>
                <iframe class="modal-iframe" id="modalIframe" src=""></iframe>
            </div>
        </div>
        
        <script>
            let currentContainerId = null;
            const refreshIntervalSeconds = 30;
            let countdown = refreshIntervalSeconds;

            const autoRefreshCheckbox = document.getElementById('autoRefreshCheckbox');
            const countdownDisplay = document.getElementById('countdown');
            
            function openModal(url, name, containerId) {{
                const modal = document.getElementById('modal');
                const modalIframe = document.getElementById('modalIframe');
                const modalTitle = document.getElementById('modalTitle');
                
                currentContainerId = containerId;
                modalIframe.src = url;
                modalTitle.textContent = name;
                modal.classList.add('active');
            }}
            
            function closeModal() {{
                const modal = document.getElementById('modal');
                const modalIframe = document.getElementById('modalIframe');
                
                currentContainerId = null;
                modal.classList.remove('active');
                modalIframe.src = '';
            }}
            
            async function killContainer(containerId, fromModal = false) {{
                const idToKill = fromModal ? currentContainerId : containerId;
                
                if (!confirm('Are you sure you want to kill this container?')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/kill/' + idToKill, {{
                        method: 'POST'
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        alert('Container killed successfully');
                        if (fromModal) {{
                            closeModal();
                        }}
                        location.reload();
                    }} else {{
                        alert('Failed to kill container: ' + result.message);
                    }}
                }} catch (error) {{
                    alert('Error: ' + error.message);
                }}
            }}
            
            // Close modal on ESC key
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    closeModal();
                }}
            }});
            
            // Main timer loop, runs every second
            setInterval(() => {{
                const modal = document.getElementById('modal');
                
                if (autoRefreshCheckbox.checked && !modal.classList.contains('active')) {{
                    countdown--;
                    countdownDisplay.textContent = `Refreshing in ${{countdown}}s...`;
                    
                    if (countdown <= 0) {{
                        location.reload();
                    }}
                }} else {{
                    countdown = refreshIntervalSeconds; // Reset for when it resumes
                    if (modal.classList.contains('active')) {{
                        countdownDisplay.textContent = 'Paused (modal open)';
                    }} else {{
                        countdownDisplay.textContent = 'Auto-refresh disabled';
                    }}
                }}
            }}, 1000);

            // Handle checkbox changes
            autoRefreshCheckbox.addEventListener('change', function() {{
                localStorage.setItem('autoRefreshEnabled', this.checked);
                if (this.checked) {{
                    countdown = refreshIntervalSeconds; // Reset countdown on re-enable
                }}
            }});

            // On page load, set checkbox from memory
            document.addEventListener('DOMContentLoaded', () => {{
                // Defaults to true if no setting is found
                const isAutoRefreshEnabled = localStorage.getItem('autoRefreshEnabled') !== 'false';
                autoRefreshCheckbox.checked = isAutoRefreshEnabled;
            }});

        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/api/containers")
async def get_containers():
    """API endpoint to get container list as JSON"""
    return {"containers": get_neko_containers()}

@app.post("/api/kill/{container_id}")
async def kill_container(container_id: str):
    """Kill a container by ID"""
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        container.kill()
        return {"success": True, "message": f"Container {container_id} killed"}
    except Exception as e:
        return {"success": False, "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8731)