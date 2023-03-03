#!/bin/bash

MY_IP=$(ip addr show | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1 -d'/')
TOKEN=$(grep -w $MY_IP "/root/My-App/tokens.txt" | awk '{print $2}')

#Script

sed -i 's/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMHg0RkVDRjhlZThlMEI0NTc4QTQ2NDc4OWM0NjFCODJCNTY1NzRBNjVFIiwicm9sZSI6InVzZXJfcm9sZSIsImF1ZCI6InBvc3RncmFwaGlsZSIsImlhdCI6MTY3NzA1NDc5OH0.EfZL8hNQH1P_Sr3G2thlsvfYUt4czjfPFQLLeEx4r0U/'$TOKEN'/g' /root/My-App/bot.py
