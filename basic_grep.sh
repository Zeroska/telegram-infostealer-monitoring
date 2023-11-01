list_of_email_need_to_grep = ("@opswat.com", "@coinhako.com", "@hdbank.com", "@mservices.com") 

for emails in ${list_of_email_need_to_grep[@]};do
  # Start a TMUX session for each grep commmand that have the keywords
  tmux split-windows -v bash -grep "emails"
done
