// API Base URL
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Navigation
document.addEventListener('DOMContentLoaded', () => {
    // Setup navigation
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('.section');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);

            // Update active states
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));

            link.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Temperature slider
    const tempSlider = document.getElementById('temperature');
    const tempValue = document.getElementById('temp-value');
    if (tempSlider && tempValue) {
        tempSlider.addEventListener('input', (e) => {
            tempValue.textContent = e.target.value;
        });
    }

    // Load initial data
    loadProjects();
    loadDeployments();
});

// Project Management
async function createProject() {
    const name = prompt('Enter project name:');
    if (!name) return;

    const description = prompt('Enter project description:');
    const useCase = prompt('Enter use case:');

    try {
        const response = await fetch(`${API_BASE_URL}/projects/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                description,
                customer_id: 'customer_' + Date.now(),
                use_case: useCase || 'general',
                llm_providers: ['openai']
            })
        });

        if (response.ok) {
            alert('Project created successfully!');
            loadProjects();
        } else {
            alert('Failed to create project');
        }
    } catch (error) {
        console.error('Error creating project:', error);
        alert('Error: Could not connect to API. Make sure the backend is running.');
    }
}

async function loadProjects() {
    try {
        const response = await fetch(`${API_BASE_URL}/projects/`);
        if (response.ok) {
            const projects = await response.json();
            // Update UI with projects
            console.log('Projects loaded:', projects);
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function loadDeployments() {
    try {
        const response = await fetch(`${API_BASE_URL}/deployments/`);
        if (response.ok) {
            const deployments = await response.json();
            // Update UI with deployments
            console.log('Deployments loaded:', deployments);
        }
    } catch (error) {
        console.error('Error loading deployments:', error);
    }
}

// LLM Console
async function generateCompletion() {
    const prompt = document.getElementById('prompt').value;
    const provider = document.getElementById('provider').value;
    const model = document.getElementById('model').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const responseBox = document.getElementById('response');
    const usageDiv = document.getElementById('usage');

    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }

    responseBox.textContent = 'Generating response...';
    usageDiv.style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/llm/completion`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt,
                provider,
                model,
                temperature
            })
        });

        if (response.ok) {
            const data = await response.json();
            responseBox.textContent = data.content;

            // Show usage information
            if (data.usage) {
                document.getElementById('token-count').textContent = data.usage.total_tokens || 0;
                const estimatedCost = (data.usage.total_tokens || 0) * 0.00002; // Rough estimate
                document.getElementById('cost').textContent = estimatedCost.toFixed(4);
                usageDiv.style.display = 'flex';
            }
        } else {
            const error = await response.json();
            responseBox.textContent = `Error: ${error.detail || 'Failed to generate completion'}`;
        }
    } catch (error) {
        console.error('Error generating completion:', error);
        responseBox.textContent = 'Error: Could not connect to API. Make sure the backend is running at ' + API_BASE_URL;
    }
}

// Agent Execution
async function executeAgent(agentType) {
    const instruction = prompt(`Enter task instruction for ${agentType} agent:`);
    if (!instruction) return;

    try {
        const response = await fetch(`${API_BASE_URL}/agents/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent_type: agentType,
                instruction,
                max_iterations: 5
            })
        });

        if (response.ok) {
            const result = await response.json();
            alert(`Agent executed successfully!\n\nTask ID: ${result.task_id}\nStatus: ${result.status}`);
        } else {
            alert('Failed to execute agent');
        }
    } catch (error) {
        console.error('Error executing agent:', error);
        alert('Error: Could not connect to API. Make sure the backend is running.');
    }
}

// Model selection based on provider
document.getElementById('provider')?.addEventListener('change', (e) => {
    const modelSelect = document.getElementById('model');
    const provider = e.target.value;

    if (provider === 'openai') {
        modelSelect.innerHTML = `
            <option value="gpt-4">GPT-4</option>
            <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
        `;
    } else if (provider === 'anthropic') {
        modelSelect.innerHTML = `
            <option value="claude-3-opus-20240229">Claude 3 Opus</option>
            <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
            <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
        `;
    }
});

// Auto-refresh deployment metrics
setInterval(() => {
    const activeSection = document.querySelector('.section.active');
    if (activeSection && activeSection.id === 'deployments') {
        loadDeployments();
    }
}, 30000); // Refresh every 30 seconds
