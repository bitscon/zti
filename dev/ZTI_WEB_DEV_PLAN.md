# Dev Website Deployment Plan

## Target
- **URL:** http://zti.barn.workshop.home/dev/site/
- **Source:** /home/billyb/workspaces/zerotrustintelligence/dev/site/

---

## Step 1: Create Nginx Config

```bash
sudo tee /etc/nginx/sites-available/zti.barn.workshop.home > /dev/null << 'EOF'
server {
    listen 80;
    server_name zti.barn.workshop.home;

    alias /home/billyb/workspaces/zerotrustintelligence/dev/site;
    index index.html;

    location /dev/site/ {
        try_files $uri $uri/ $uri/index.html =404;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1h;
        add_header Cache-Control "public";
    }
}
EOF
```

---

## Step 2: Add DNS Entry

```bash
sudo sh -c 'echo "127.0.0.1  zti.barn.workshop.home" >> /etc/hosts'
```

---

## Step 3: Enable Site & Reload Nginx

```bash
sudo ln -sf /etc/nginx/sites-available/zti.barn.workshop.home /etc/nginx/sites-enabled/
sudo nginx -t
sudo nginx -s reload
```

---

## Verify

Open: http://zti.barn.workshop.home/dev/site/