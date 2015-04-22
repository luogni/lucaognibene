;; defaults
(setq fab-path "fab")

(load-file "~/.private.el")

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(custom-safe-themes
   (quote
    ("a041a61c0387c57bb65150f002862ebcfe41135a3e3425268de24200b82d6ec9" "e80932ca56b0f109f8545576531d3fc79487ca35a9a9693b62bf30d6d08c9aaf" "764e3a6472a3a4821d929cdbd786e759fab6ef6c2081884fca45f1e1e3077d1d" default)))
 '(elfeed-feeds
   (quote
    ("http://192.168.5.111/trac/timeline?changeset=on&max=50&daysback=90&format=rss" "http://192.168.5.111/trac/timeline?ticket=on&ticket_details=on&max=50&daysback=90&format=rss")))
 '(elpy-modules
   (quote
    (elpy-module-company elpy-module-eldoc elpy-module-flymake elpy-module-pyvenv elpy-module-yasnippet elpy-module-sane-defaults)))
 '(multi-term-switch-after-close nil)
 '(package-archives
   (quote
    (("gnu" . "http://elpa.gnu.org/packages/")
     ("marmalade" . "http://marmalade-repo.org/packages/")
     ("MELPA" . "http://melpa.org/packages/"))))
 '(projectile-project-root-files
   (quote
    ("rebar.config" "project.clj" "SConstruct" "pom.xml" "build.sbt" "build.gradle" "Gemfile" "requirements.txt" "package.json" "gulpfile.js" "Gruntfile.js" "bower.json" "composer.json" "Cargo.toml" "mix.exs" "tox.ini")))
 '(show-paren-mode t)
 '(term-bind-key-alist
   (quote
    (("C-c C-c" . term-interrupt-subjob)
     ("C-c C-e" . term-send-esc)
     ("C-p" . previous-line)
     ("C-n" . next-line)
     ("C-s" . isearch-forward)
     ("C-r" . isearch-backward)
     ("C-m" . term-send-return)
     ("C-y" . term-paste)
     ("M-f" . term-send-forward-word)
     ("M-b" . term-send-backward-word)
     ("M-o" . term-send-backspace)
     ("M-p" . term-send-up)
     ("M-n" . term-send-down)
     ("M-M" . term-send-forward-kill-word)
     ("M-N" . term-send-backward-kill-word)
     ("<C-backspace>" . term-send-backward-kill-word)
     ("M-r" . term-send-reverse-search-history)
     ("M-," . term-send-raw)
     ("M-." . comint-dynamic-complete))))
 '(tool-bar-mode nil)
 '(tooltip-mode nil)
 '(type-break-interval 7200)
 '(type-break-keystroke-threshold (quote (210 . 10500)))
 '(type-break-query-mode t)
 '(vc-log-show-limit 10))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

(require 'package)
(add-to-list 'package-archives
             '("elpy" . "http://jorgenschaefer.github.io/packages/"))
(package-initialize)
(elpy-enable)

(setq circe-network-options
      `(("aycloud"
	:host "aycloud.it"
	:port (8767)
	:channels ("#aylook")
	:pass ,anteklab-password
	)))

(load-theme `ample t)
(setq ido-enable-flex-matching t)
(setq ido-everywhere t)
(ido-mode 1)

(setq-default elfeed-search-filter "-junk @1-week-ago +unread")
 
(load "lui-logging" nil t)
(enable-lui-logging-globally)

(smex-initialize)
(global-set-key (kbd "M-x") 'smex)

(autoload 'mew "mew" nil t)
(autoload 'mew-send "mew" nil t)

;; Optional setup (Read Mail menu):
(setq read-mail-command 'mew)

;; Optional setup (e.g. C-xm for sending a message):
(autoload 'mew-user-agent-compose "mew" nil t)
(if (boundp 'mail-user-agent)
    (setq mail-user-agent 'mew-user-agent))
(if (fboundp 'define-mail-user-agent)
    (define-mail-user-agent
      'mew-user-agent
      'mew-user-agent-compose
      'mew-draft-send-message
      'mew-draft-kill
      'mew-send-hook))

(setq mew-name "Luca Ognibene") ;; (user-full-name)
(setq mew-user "ognibene") ;; (user-login-name)
(setq mew-mail-domain "antek-aad.com")
(setq mew-smtp-server "smtp.antek-aad.com")  ;; if not localhost
(setq mew-proto "%")
(setq mew-mailbox-type 'imap)
(setq mew-imap-user "ognibene@antek-aad.com")  ;; (user-login-name)
(setq mew-imap-server "imap.antek-aad.com")    ;; if not localhost
(setq mew-use-biff t)
(setq mew-biff-interval 10)
(setq mew-use-cached-passwd t)

(type-break-mode 1)
(type-break-query-mode 1)

(defun ay-vpn ()
  (interactive)
  (multi-term)
  (rename-buffer "vpn")
  (comint-send-string (current-buffer) "vpnay\n")
  (comint-send-string (current-buffer) (format "%s\n" anteklab-vpn-cmd))
  )

(defun ay-fab (ip cmd)
  (interactive "sIP? \nsCMD? ")
  (multi-term)
  (comint-send-string (current-buffer) "cd ~/Progetti/aylook/trunk\n")
  (comint-send-string (current-buffer) (format "%s -H %s %s\n" fab-path ip cmd))
)  

(defun ay-start ()
  (interactive)
  (circe "aycloud")
  (ay-vpn)
;  (ay-fab "125" "deploy:what=aymaster,update=t")
  (mew)
  (elfeed)
  )

(defun ay-terminal ()
  (interactive)
  (start-process "AyTerm" nil "gnome-terminal" "--maximize")
  )

(defun ay-ssh (ip)
  (interactive "sIP? ")
  (start-process "AySSH" nil "gnome-terminal" "--maximize" "-e" (format "ayssh %s" ip))
  )

(defun ay-firefox ()
  (interactive)
  (start-process "AyFF" nil "firefox" "-P" "dev" "--new-instance")
  )

(defun ay-merge (branch revision)
  (interactive "sDestination Branch? \nsRevisions? ")
  (multi-term)
  (comint-send-string (current-buffer) (format "cd ~/Progetti/aylook/%s\n" branch))
  (comint-send-string (current-buffer) "svn update --ignore-externals\n")
  (comint-send-string (current-buffer) (format "svn merge -c %s ../trunk\n" revision))
  (comint-send-string (current-buffer) "svn diff | less")
  )

(defun pocket-put ()
  (interactive)
  (start-process "Pockyt" nil "pockyt" "put" "-i" (thing-at-point 'url))
  )

(global-set-key (kbd "C-c t") 'ay-terminal)
(global-set-key (kbd "C-c x") 'ay-firefox)
(global-set-key (kbd "C-c s") 'ay-ssh)
(global-set-key (kbd "C-c f") 'ay-fab)
(global-set-key (kbd "C-c m") 'ay-merge)
(global-set-key (kbd "C-c p") 'pocket-put)
(global-set-key (kbd "C-c w") (lambda () (interactive) (find-file "~/Dropbox/snow.org")))
(global-set-key (kbd "<f8>") 'winner-undo)
(global-set-key (kbd "C-x C-i") 'idomenu)
(global-set-key (kbd "C-x C-m") 'smex)
(global-set-key (kbd "C-c C-m") 'smex)
(global-set-key (kbd "C-c **") 'calculator)

(defalias 'yes-or-no-p 'y-or-n-p)
(scroll-bar-mode -1)
(winner-mode 1)

(setq twittering-use-master-password t)
