# cowin_bot_source_code
This selenium based bot will keep polling cowin website to check and notify on vaccine slot availability

# How to use?
Update 'config.yaml' file with the 'pin code' and 'vaccination center name'
Example1: Pin code with center names
```
416410:
  - SAMATANAGAR
  - MIRAJ URBAN
```

Example2: Pin code without center names, it will check all available centers in that pin code
```
416416:
```
Then trigger the 'cowin_selenium.py' file
Now it will keep on checking all the vaccination centers for slots availability,
An alarm will be triggered when it will detect any slot
