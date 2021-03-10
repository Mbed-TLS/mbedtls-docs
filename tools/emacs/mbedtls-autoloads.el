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

(provide 'mbedtls-autoloads)

;;; That's all.
