# 1. Base Image
FROM us-docker.pkg.dev/google-appengine-images/python/python312

# 2. Set APP_HOME
ENV APP_HOME /srv
WORKDIR $APP_HOME

# 3. Copy Requirements
COPY requirements.txt .

# 4. Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
COPY . .


