## Kosmo Chatbot (Kinyarwanda)

Chatbot yunganira mu gusubiza ibibazo byerekeye imihango, gusama/utwite, n'irerero ry'umwana mu Kinyarwanda, ikoresheje ububiko bw'amakuru (KB) n'ihurizo rishingiye ku gushaka ibisa (fuzzy matching).

### Uko bikora
- Ukoresheje Streamlit kubaka interineti yoroshye.
- Ububiko (`data/kb.csv`) bubika Q&A mu Kinyarwanda.
- RapidFuzz ikoreshwa gushaka ibibazo bisa n'ibyo wabajije no kugarura igisubizo kijyanye.
- Sidebar igufasha kongeramo ibibazo n'ibisubizo byawe byihuse.

### Gukoresha
1. Tekinika (Python 3.9+ irasabwa):
   - Windows PowerShell:
     - Kora virtualenv:
       ```powershell
       python -m venv .venv
       .\.venv\Scripts\Activate.ps1
       ```
     - Shyiramo dependencies:
       ```powershell
       python -m pip install -U pip
       pip install -r requirements.txt
       ```
     - Tangira app:
       ```powershell
       streamlit run app.py
       ```

2. Fungura mu mucukumbuzi (browser) aho Streamlit igaragaza `Local URL`.

### Guhindura/Kongeramo Amakuru
- Gukoresha ifishi iri kuri sidebar kongeramo Q&A bishya.
- Cyangwa uhindure `data/kb.csv` mu buryo bwa CSV (UTF-8), ukongera gutangiza app.

### Icyitonderwa
- Ibisubizo bitangwa ni rusange kandi si inama z'ubuvuzi. Mu gihe ukeneye ubufasha bwihuse cyangwa ibimenyetso bikomeye, jya kwa muganga.


## Backend API (FastAPI)

- Run locally:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

- Endpoints:
  - GET `/health` → `{ "status": "ok" }`
  - POST `/chat` → request: `{ "query": "..." }`, response: `{ "answer": "..." }`
  - GET `/kb?limit=100&offset=0` → list KB
  - POST `/kb` → `{ "question": "...", "answer": "...", "tags": "a,b" }`

## Docker (Backend only)

- Build image:
```bash
docker build -t kosmo-backend:latest .
```
- Run container:
```bash
docker run -p 8000:8000 --name kosmo-backend kosmo-backend:latest
```

## Deploy on Render

There is a `render.yaml` blueprint for one-click setup with a persistent disk for `data/kb.csv`.

### Steps (Blueprint)
1. Push this repo to GitHub/GitLab.
2. In Render, click New → Blueprint.
3. Connect the repo and choose the branch containing `render.yaml`.
4. Review settings:
   - Service name: `kosmo-chatbot-api`
   - Runtime: Docker (uses provided `Dockerfile`)
   - Health check: `/health`
   - Disk: `kb-data` mounted at `/app/data` (persists `kb.csv`)
5. Click Apply. Wait for build and deploy to finish.

### Verify
- Open the Render service URL and check `GET /health` returns `{ "status": "ok" }`.
- Test chat endpoint:
```bash
curl -s -X POST "$RENDER_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Imihango isanzwe igira igihe kingana gute?"}'
```

### Notes
- Persistence: The KB (`data/kb.csv`) survives restarts because the disk is mounted at `/app/data`.
- Entry point: Uvicorn runs `server:app` on port 8000 (see `Dockerfile`).
- Scaling: On Free plan, 1 instance; you can scale up in Render settings.

## Deploy on AWS (ECS Fargate)

1. Push image to ECR:
```bash
aws ecr create-repository --repository-name kosmo-backend || true
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=$(aws configure get region)
ECR_URI=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/kosmo-backend
aws ecr get-login-password | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag kosmo-backend:latest $ECR_URI:latest
docker push $ECR_URI:latest
```
2. Create ECS Fargate Service:
   - Task definition: container image `$ECR_URI:latest`, port 8000, CPU 256, Memory 512.
   - Service: desired count 1–2, platform Fargate.
   - Networking: attach to a VPC subnets + security group allowing TCP 80/443 (and 8000 if needed internally).
   - Load balancer (recommended): Application Load Balancer → target group on port 8000 → health check path `/health`.

3. Domain (optional): Route 53 A-record → ALB.

4. Environment/Storage:
   - Data file `data/kb.csv` is written inside the container. For persistence, mount an EFS volume or store KB in an external DB/API.

## Frontend Integration

- POST to the API endpoint (replace host with your ALB or public IP):
```bash
curl -s -X POST "https://YOUR_HOST/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Imihango isanzwe igira igihe kingana gute?"}'
```
- Response example:
```json
{ "answer": "..." }
```



