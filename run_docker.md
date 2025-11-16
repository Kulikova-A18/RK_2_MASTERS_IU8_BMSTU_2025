# run docker

clean all

```
sudo docker system prune -a --volumes
```

run

```
sudo docker-compose up --force-recreate --build -d
```

show log

```
sudo docker-compose logs -f rk2_app_standalone
```