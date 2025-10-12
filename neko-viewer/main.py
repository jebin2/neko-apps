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
            @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Press Start 2P', monospace;
                background: #1a0d2e;
                color: #00ff88;
                padding: 20px;
                overflow-x: hidden;
                position: relative;
                image-rendering: pixelated;
                image-rendering: -moz-crisp-edges;
                image-rendering: crisp-edges;
            }}
            
            body::before {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: 
                    repeating-linear-gradient(
                        0deg,
                        rgba(0, 255, 136, 0.03) 0px,
                        transparent 1px,
                        transparent 2px,
                        rgba(0, 255, 136, 0.03) 3px
                    );
                pointer-events: none;
                z-index: 1;
                animation: scanlines 8s linear infinite;
            }}
            
            @keyframes scanlines {{
                0% {{ transform: translateY(0); }}
                100% {{ transform: translateY(4px); }}
            }}
            
            h1 {{
                text-align: center;
                margin-bottom: 25px;
                color: #ff3366;
                font-size: 24px;
                text-shadow: 
                    3px 3px 0px #00ff88,
                    6px 6px 0px rgba(0, 255, 136, 0.3);
                letter-spacing: 2px;
                position: relative;
                z-index: 2;
                animation: glitch 3s infinite;
            }}
            
            @keyframes glitch {{
                0%, 90%, 100% {{
                    transform: translate(0);
                }}
                92% {{
                    transform: translate(-2px, 2px);
                }}
                94% {{
                    transform: translate(2px, -2px);
                }}
                96% {{
                    transform: translate(-2px, -2px);
                }}
            }}

            .controls {{
                text-align: center;
                margin-bottom: 30px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 20px;
                color: #00ff88;
                position: relative;
                z-index: 2;
                font-size: 10px;
            }}

            .controls label {{
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                padding: 8px 12px;
                background: rgba(255, 51, 102, 0.1);
                border: 2px solid #ff3366;
                box-shadow: 0 0 10px rgba(255, 51, 102, 0.3);
            }}
            
            .controls label:hover {{
                background: rgba(255, 51, 102, 0.2);
                box-shadow: 0 0 20px rgba(255, 51, 102, 0.5);
            }}
            
            input[type="checkbox"] {{
                width: 16px;
                height: 16px;
                cursor: pointer;
                accent-color: #ff3366;
            }}

            #countdown {{
                font-weight: 600;
                min-width: 200px;
                text-align: center;
                color: #00ff88;
                text-shadow: 0 0 10px rgba(0, 255, 136, 0.8);
            }}
            
            .grid-container {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
                gap: 25px;
                max-width: 1600px;
                margin: 0 auto;
                position: relative;
                z-index: 2;
            }}
            
            .grid-item {{
                background: #0f0820;
                border: 3px solid #ff3366;
                box-shadow: 
                    0 0 20px rgba(255, 51, 102, 0.4),
                    inset 0 0 20px rgba(0, 255, 136, 0.1);
                overflow: hidden;
                cursor: pointer;
                transition: all 0.3s;
                position: relative;
            }}
            
            .grid-item::before {{
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, #ff3366, #00ff88, #ff3366);
                z-index: -1;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            
            .grid-item:hover {{
                transform: translateY(-8px);
                box-shadow: 
                    0 0 40px rgba(255, 51, 102, 0.6),
                    0 0 60px rgba(0, 255, 136, 0.4),
                    inset 0 0 30px rgba(0, 255, 136, 0.2);
            }}
            
            .grid-item:hover::before {{
                opacity: 0.3;
            }}
            
            .grid-header {{
                padding: 15px;
                background: linear-gradient(135deg, #0f0820 0%, #1a0d2e 100%);
                border-bottom: 3px solid #00ff88;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .header-info {{
                flex: 1;
            }}
            
            .kill-btn {{
                background: linear-gradient(135deg, #cc0052 0%, #ff3366 100%);
                color: #ffffff;
                border: 2px solid #ff3366;
                padding: 8px 15px;
                cursor: pointer;
                font-size: 8px;
                font-family: 'Press Start 2P', monospace;
                transition: all 0.3s;
                margin-left: 10px;
                box-shadow: 0 0 10px rgba(255, 51, 102, 0.5);
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }}
            
            .kill-btn:hover {{
                background: linear-gradient(135deg, #ff3366 0%, #ff3366 100%);
                box-shadow: 0 0 20px rgba(255, 51, 102, 0.8);
                transform: scale(1.05);
            }}
            
            .container-name {{
                font-weight: 600;
                font-size: 11px;
                margin-bottom: 8px;
                color: #ff3366;
                text-shadow: 0 0 10px rgba(255, 51, 102, 0.6);
            }}
            
            .container-port {{
                font-size: 8px;
                color: #00ff88;
                text-shadow: 0 0 5px rgba(0, 255, 136, 0.6);
            }}
            
            .iframe-container {{
                width: 100%;
                height: 300px;
                position: relative;
                overflow: hidden;
                border: 2px solid #00ff88;
                background: #000;
            }}
            
            .grid-item iframe {{
                width: 100%;
                height: 100%;
                border: none;
                pointer-events: none;
                filter: contrast(1.1) saturate(1.2);
            }}
            
            .modal {{
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(15, 8, 32, 0.95);
                z-index: 1000;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
            }}
            
            .modal.active {{
                display: flex;
            }}
            
            .modal-content {{
                width: 95%;
                height: 95%;
                position: relative;
                background: #0f0820;
                border: 4px solid #ff3366;
                box-shadow: 
                    0 0 50px rgba(255, 51, 102, 0.6),
                    0 0 100px rgba(0, 255, 136, 0.3),
                    inset 0 0 30px rgba(0, 255, 136, 0.1);
                overflow: hidden;
            }}
            
            .modal-header {{
                padding: 20px;
                background: linear-gradient(135deg, #0f0820 0%, #1a0d2e 100%);
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #00ff88;
            }}
            
            .modal-actions {{
                display: flex;
                gap: 15px;
            }}
            
            .kill-btn-modal {{
                background: linear-gradient(135deg, #cc0052 0%, #ff3366 100%);
                color: #ffffff;
                border: 2px solid #ff3366;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 10px;
                font-family: 'Press Start 2P', monospace;
                transition: all 0.3s;
                box-shadow: 0 0 15px rgba(255, 51, 102, 0.5);
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
            }}
            
            .kill-btn-modal:hover {{
                background: linear-gradient(135deg, #ff3366 0%, #ff3366 100%);
                box-shadow: 0 0 25px rgba(255, 51, 102, 0.8);
                transform: scale(1.05);
            }}
            
            .modal-title {{
                font-size: 12px;
                font-weight: 600;
                color: #ff3366;
                text-shadow: 0 0 10px rgba(255, 51, 102, 0.8);
            }}
            
            .close-btn {{
                background: linear-gradient(135deg, #00aa5e 0%, #00ff88 100%);
                color: #000;
                border: 2px solid #00ff88;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 10px;
                font-family: 'Press Start 2P', monospace;
                font-weight: 600;
                transition: all 0.3s;
                box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
                text-shadow: 1px 1px 2px rgba(255, 255, 255, 0.5);
            }}
            
            .close-btn:hover {{
                background: linear-gradient(135deg, #00ff88 0%, #00ff88 100%);
                box-shadow: 0 0 25px rgba(0, 255, 136, 0.8);
                transform: scale(1.05);
            }}
            
            .modal-iframe {{
                width: 100%;
                height: calc(100% - 80px);
                border: none;
                border-top: 2px solid #00ff88;
                background: #000;
            }}
            
            .no-containers {{
                text-align: center;
                padding: 60px 20px;
                color: #ff3366;
                font-size: 14px;
                text-shadow: 0 0 20px rgba(255, 51, 102, 0.8);
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.6; }}
            }}
        </style>
    </head>
    <body>
        <h1>▓▒░ NEKO DOCKERS ░▒▓</h1>
        
        <div class="controls">
            <label for="autoRefreshCheckbox">
                <input type="checkbox" id="autoRefreshCheckbox">
                AUTO REFRESH
            </label>
            <span id="countdown"></span>
        </div>

        <div class="grid-container" id="gridContainer">
            {''.join([f'''
            <div class="grid-item" onclick="openModal('{c['url']}', '{c['name']}', '{c['id']}')">
                <div class="grid-header">
                    <div class="header-info">
                        <div class="container-name">▸ {c['name']}</div>
                        <div class="container-port">PORT: {c['port']} | ID: {c['id']}</div>
                    </div>
                    <button class="kill-btn" onclick="event.stopPropagation(); killContainer('{c['id']}')">✖ KILL</button>
                </div>
                <div class="iframe-container">
                    <iframe src="{c['url']}" loading="lazy"></iframe>
                </div>
            </div>
            ''' for c in containers]) if containers else '<div class="no-containers">▓▒░ NO NEKO CONTAINERS RUNNING ░▒▓</div>'}
        </div>
        
        <div class="modal" id="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title" id="modalTitle"></div>
                    <div class="modal-actions">
                        <button class="kill-btn-modal" id="modalKillBtn" onclick="killContainer(null, true)">✖ KILL</button>
                        <button class="close-btn" onclick="closeModal()">✕ CLOSE</button>
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
                modalTitle.textContent = '▸ ' + name;
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
                
                if (!confirm('ARE YOU SURE YOU WANT TO KILL THIS CONTAINER?')) {{
                    return;
                }}
                
                try {{
                    const response = await fetch('/api/kill/' + idToKill, {{
                        method: 'POST'
                    }});
                    
                    const result = await response.json();
                    
                    if (result.success) {{
                        alert('CONTAINER KILLED SUCCESSFULLY');
                        if (fromModal) {{
                            closeModal();
                        }}
                        location.reload();
                    }} else {{
                        alert('FAILED TO KILL CONTAINER: ' + result.message);
                    }}
                }} catch (error) {{
                    alert('ERROR: ' + error.message);
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
                    countdownDisplay.textContent = `REFRESHING IN ${{countdown}}S...`;
                    
                    if (countdown <= 0) {{
                        location.reload();
                    }}
                }} else {{
                    countdown = refreshIntervalSeconds;
                    if (modal.classList.contains('active')) {{
                        countdownDisplay.textContent = 'PAUSED (MODAL OPEN)';
                    }} else {{
                        countdownDisplay.textContent = 'AUTO-REFRESH DISABLED';
                    }}
                }}
            }}, 1000);

            // Handle checkbox changes
            autoRefreshCheckbox.addEventListener('change', function() {{
                localStorage.setItem('autoRefreshEnabled', this.checked);
                if (this.checked) {{
                    countdown = refreshIntervalSeconds;
                }}
            }});

            // On page load, set checkbox from memory
            document.addEventListener('DOMContentLoaded', () => {{
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