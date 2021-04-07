;;; mbedtls-autoloads -- definitions for Mbed TLS development

;; Add the directory containing this file to your `load-path` and
;; put (require 'mbedtls-autoloads) in your Emacs init file.

;;; Code:

;; Mbed TLS test data mode
(add-to-list 'auto-mode-alist
             '("mbedtls.*/.*\\.data\\'" . mbedtls-test-data-mode))
(autoload 'mbedtls-test-data-mode "mbedtls-test-data-mode"
  "Major mode to edit Mbed TLS test data files."
  t)

;; .function files are C code
(add-to-list 'auto-mode-alist '("/suites/[^/]+\\.function\\'" . c-mode))

;; Mbed TLS indentation style

(defun cc-style-lineup-if-with-else (context)
  "When there is a newline in else/if, indent if like else.
That is, indent like this:
    if (...)
        ...
    else
    if (...)
        ...
instead of this:
    if (...)
        ...
    else
        if (...)
            ...
To achieve this, add `(substatement cc-style-lineup-if-with-else +)'
to `c-offsets-alist'."
  ;; https://emacs.stackexchange.com/questions/31038/stop-reindenting-if-after-else/31041#31041
  (pcase context
    (`(substatement . ,anchor)
     (save-excursion
       (back-to-indentation)
       (when (looking-at-p "if\\_>")
         (goto-char anchor)
         (when (looking-at-p "\\(else\\|switch\\)\\_>")
           0))))))

(defun cc-style-make-mbedtls ()
  (let ((entry (assoc "mbedtls" c-style-alist)))
    (unless entry
      (setq entry (cons "mbedtls" nil))
      (setq c-style-alist (cons entry c-style-alist)))
    (setcdr entry '((c-basic-offset . 4)
                    (c-hanging-braces-alist
                     (arglist-cont before after)
                     (arglist-cont-nonempty before after)
                     (substatement-open before after))
                    (c-offsets-alist
                     (case-label . +)
                     (inextern-lang . 0)
                     (label . 0)
                     (substatement cc-style-lineup-if-with-else +)
                     (substatement-open . 0)
                     (substatement-label . 0)
                     )))))
(eval-after-load "cc-styles" '(cc-style-make-mbedtls))

(provide 'mbedtls-autoloads)

;;; That's all.
