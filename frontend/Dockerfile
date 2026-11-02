
FROM node:22-alpine

WORKDIR /app

# Copy dependency definitions
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy application source
COPY . .

# Expose Next.js
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
