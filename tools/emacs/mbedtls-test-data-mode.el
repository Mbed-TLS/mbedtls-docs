;;; mbedtls-test-data-mode.el --- mode for Mbed TLS test data files

;;; Code:

(defvar mbedtls-test-data-mode-syntax-table
  (let ((table (make-syntax-table)))
    (modify-syntax-entry ?\n ">" table)
    (modify-syntax-entry ?\" "\"" table)
    table)
  "Syntax table to use in Mbed TLS test data mode.")

(defvar mbedtls-test-data-functions nil
  "List of test functions available for this data file.
Each element of the list has the form (NAME ARGUMENTS).
NAME is the name of the test function.
ARGUMENTS is a vector of argument names.")
(make-variable-buffer-local 'mbedtls-test-data-functions)

(defvar mbedtls-test-data-function-buffer nil
  "Buffer visiting the associated .function file.")
(make-variable-buffer-local 'mbedtls-test-data-function-buffer)

(defun mbedtls-test-data-function-file-name (&optional data-file)
  "Return the name of the .function file associated with the current .data file.
With no argument or with nil as an argument, use the current buffer's file name.
If the optional argument DATA-FILE is a buffer, use its buffer file name.
If the optional argument DATA-FILE is a string, use that as the name of the
.data file."
  (let ((file-name (if (stringp data-file)
                       data-file
                     (buffer-file-name data-file)))
        (case-fold-search t))
    (save-match-data
      (if (string-match "\\(\\.[-0-9A-Z_a-z]+\\)?\\.data\\'" file-name)
          (setq file-name (substring file-name 0 (match-beginning 0)))))
    (concat file-name ".function")))

(defun mbedtls-test-data-visit-function-file (&optional data-file
                                                        no-error
                                                        select)
  "Visit the .function file associated with the current .data file.
Return the buffer visiting the file.
Interpret optional argument DATA-FILE as `mbedtls-test-data-visit-function-file'.
If the optional argument NO-ERROR is non-nil, don't error out if the file
cannot be visited, just return nil.
If the optional argument SELECT is non-nil, display the buffer. This is the
default when this function is called interactively."
  (interactive '(nil nil t))
  (let ((filename (mbedtls-test-data-function-file-name data-file)))
    (cond
     (select (find-file filename))
     (no-error (condition-case nil
                   (find-file-noselect filename t)
                 (error nil)))
     (t (find-file-noselect filename t)))))

(defun mbedtls-test-data-parse-function-argument-name (function-data limit)
  (let ((found nil))
    (while (and (< limit (point))
                (not (setq found (looking-at "[0-9A-Z_a-z]+"))))
      (condition-case nil
          (backward-sexp)
        ;; "Containing expression ends prematurely" on an empty
        ;; parameter list.
        (scan-error (goto-char limit))))
    (if found
        (setcdr function-data (cons (substring-no-properties (match-string 0))
                                    (cdr function-data))))))

(defun mbedtls-test-data-parse-function-file-contents ()
  (let ((entries nil)
        (case-fold-search nil))
    (while (search-forward-regexp "^/\\*\\s-+BEGIN_CASE\\>" nil t)
      (forward-line)
      (when (looking-at "[^\n()]*\\s-\\([0-9A-Z_a-z]+\\)\\s-*(")
        (let ((function-data (list (substring-no-properties (match-string 1))))
              (arguments-start (match-end 0)))
          (goto-char (1- (match-end 0)))
          (forward-sexp)
          (backward-char)
          (mbedtls-test-data-parse-function-argument-name function-data
                                                          arguments-start)
          (when (cdr function-data)
            (while (search-backward "," arguments-start t)
              (mbedtls-test-data-parse-function-argument-name function-data
                                                              arguments-start)))
          (setq entries (cons (list (car function-data)
                                    (apply #'vector (cdr function-data)))
                              entries)))))
    entries))

(defun mbedtls-test-data-parse-function-file (&optional no-error)
  "Parse the .function file associated with the current .data file.
Store the results in `mbedtls-test-data-functions'.
If NO-ERROR is non-nil, do nothing if the .function file cannot be visited."
  (interactive "@")
  (or (buffer-live-p mbedtls-test-data-function-buffer)
      (setq mbedtls-test-data-function-buffer
            (mbedtls-test-data-visit-function-file nil no-error)))
  (when mbedtls-test-data-function-buffer
    (save-match-data
      (with-current-buffer mbedtls-test-data-function-buffer
        (save-excursion
          (save-restriction
            (widen)
            (goto-char (point-min))
            (setq mbedtls-test-data-functions
                  (mbedtls-test-data-parse-function-file-contents))))))))

(defun mbedtls-test-data-get-functions ()
  "Return information about available test functions.
This is the value of `mbedtls-test-data-functions' in the associated .function
buffer.
Use a cached result if available. Call `mbedtls-test-data-parse-function-file'
to update the cache."
  (or (buffer-live-p mbedtls-test-data-function-buffer)
      (setq mbedtls-test-data-function-buffer
            (mbedtls-test-data-visit-function-file nil t)))
  (when mbedtls-test-data-function-buffer
    (with-current-buffer mbedtls-test-data-function-buffer
      (or mbedtls-test-data-functions
          (mbedtls-test-data-parse-function-file t))
      mbedtls-test-data-functions)))

(defun mbedtls-test-data-backward-argument (&optional arg)
  "Move backward to after the previous `:'.
With a prefix argument, repeat that many times. If the prefix argument is
negative, call `mbedtls-test-data-forward-argument' to move backward."
  (interactive "@p")
  (if (< arg 0)
      (mbedtls-test-data-forward-argument (- n))
    (while (> arg 0)
      (backward-char)
      (skip-chars-backward "^:\n")
      (setq arg (1- arg)))))

(defun mbedtls-test-data-forward-argument (&optional arg)
  "Move forward to after the next `:'.
With a prefix argument, repeat that many times. If the prefix argument is
negative, call `mbedtls-test-data-backward-argument' to move backward."
  (interactive "@p")
  (if (< arg 0)
      (mbedtls-test-data-backward-argument (- n))
    (while (> arg 0)
      (skip-chars-forward "^:\n")
      (forward-char)
      (setq arg (1- arg)))))

(defun mbedtls-test-data-goto-function-line ()
  "Move point to the start of the line containing the function and its arguments."
  (interactive "@")
  (forward-paragraph)
  (if (bolp)
      (forward-line -1)
    (beginning-of-line)))

(defun mbedtls-test-data-get-function-name-at-point ()
  "Return the name of the test function in the test case containing point."
  (save-excursion
    (mbedtls-test-data-goto-function-line)
    (let ((beg (point)))
      (skip-chars-forward "^:\n")
      (buffer-substring-no-properties beg (point)))))

(defun mbedtls-test-data-get-function-information-at-point ()
  "Return information about the test function in the test case containing point.
This is the relevant element from `mbedtls-test-data-functions'."
  (let ((info (mbedtls-test-data-get-functions)))
    (and info
         (assoc (mbedtls-test-data-get-function-name-at-point) info))))

(defun mbedtls-test-data-show-function-information (info arg)
  (let ((argument-names (cadr info)))
    (cond
     ((or (null arg) (<= arg 0))
      (message "%s %s"
               (car info)
               (mapconcat #'identity argument-names " ")))
     ((> arg (length argument-names))
      (message "%s takes %d arguments (no argument %d)"
               (car info) (length argument-names) arg))
     (t
      (message "%d: %s" arg (aref argument-names (1- arg)))))))

(defun mbedtls-test-data-show-argument-information (&optional arg)
  "Show the name of the argument around point.
With a prefix argument, or if point is not on a function argument, show
information about the function called by this test case."
  (interactive "@P")
  (let ((original-point (point))
        (all-info (mbedtls-test-data-get-functions)))
    (when all-info
      (save-excursion
        (mbedtls-test-data-goto-function-line)
        (let* ((beg (point))
               (function-name (progn
                                (skip-chars-forward "^:\n")
                                (buffer-substring-no-properties beg (point))))
               (function-info (assoc function-name all-info))
               (pos (if (> original-point (point))
                        (cl-count ?: (buffer-substring-no-properties
                                      beg original-point))
                      0)))
          (mbedtls-test-data-show-function-information function-info pos))))))

(defun mbedtls-test-data-visit-function-definition (&optional arg)
  "Visit the function definition for the current test case.

With just \\[universal-argument] or a numerical prefix argument between 1 and 4,
visit in another window with `switch-to-buffer-other-window'. With two
\\[universal-argument] or a numerical prefix argument larger than 4, visit
in another frame with `switch-to-buffer-other-frame'. With a negative prefix
argument, don't display the function definition, only load the file and set
point in the buffer visiting it. In any case, return the function file buffer."
  (interactive "@p")
  (let ((function-name (mbedtls-test-data-get-function-name-at-point)))
    (if function-name
        (let ((buffer (mbedtls-test-data-visit-function-file))
              (switch-function (cond
                                ((null arg) 'switch-to-buffer)
                                ((symbolp arg) arg)
                                ((and (integerp arg) (> arg 4))
                                 'switch-to-buffer-other-frame)
                                ((and (integerp arg) (> arg 1))
                                 'switch-to-buffer-other-window)
                                ((and (integerp arg) (< arg 0)) 'ignore)
                                (t 'switch-to-buffer))))
          (with-current-buffer buffer
            (funcall switch-function buffer)
            (push-mark)
            (goto-char (point-min))
            (search-forward-regexp "^ */\\*+ *BEGIN_CASE\\b")
            (save-match-data
              (search-forward-regexp (concat "^\\w[^\n()]*\\s-"
                                             function-name
                                             "\\s-*("))
              (backward-char)
              (forward-sexp)
              (forward-line))
            buffer))
      (message "Unable to determine the test case function name"))))

(defun mbedtls-test-data-copy-to-top ()
  "Copy the current test case to the top of the file."
  (interactive "@*")
  (save-excursion
    (save-restriction
      (let* ((begin (progn (backward-paragraph)
                           (skip-chars-forward "\n")
                           (point)))
             (end (progn (forward-paragraph)
                         (point)))
             (text (buffer-substring-no-properties begin end)))
        (goto-char (point-min))
        (insert text "\n#### ^^^^ Temporary copy ^^^^ ####\n\n")
        (if (interactive-p)
            (message "Copied %s"
                     (save-match-data
                       (substring text 0 (string-match "\n" text)))))))))

(defvar mbedtls-test-data-mode-font-lock-keywords
  '(
    ("^#.*$" (0 font-lock-comment-face))
    ("^depends_on:"
     (0 font-lock-keyword-face)
     ("[^\n:]+" () ()
      (0 font-lock-builtin-face)))
    ("^\\([A-Z_a-z][0-9A-Z_a-z]*\\)\\(:\\)"
     (1 font-lock-function-name-face)
     (2 font-lock-keyword-face))
    (":" (0 font-lock-keyword-face))
    (".\\{66\\}\\(.+\\)"
     (1 font-lock-warning-face))
    )
  "Value of `font-lock-keywords' in Mbed TLS test data mode.")

(defvar mbedtls-test-data-mode-font-lock-defaults
  '(mbedtls-test-data-mode-font-lock-keywords
    t
    nil
    ((?_ . "w")))
  "Value of `font-lock-defaults' in Mbed TLS test data mode.")

(defvar mbedtls-test-data-mode-map
  (let ((map (make-sparse-keymap)))
    (substitute-key-definition 'backward-sentence
                               'mbedtls-test-data-backward-argument
                               map global-map)
    (substitute-key-definition 'forward-sentence
                               'mbedtls-test-data-forward-argument
                               map global-map)
    (define-key map "\C-c\C-a" 'mbedtls-test-data-show-argument-information)
    (define-key map "\C-c\C-f" 'mbedtls-test-data-visit-function-definition)
    (define-key map "\C-c\C-n" 'mbedtls-test-data-parse-function-file)
    (define-key map "\C-c\C-t" 'mbedtls-test-data-copy-to-top)
    map)
  "Keymap used in Mbed TLS test data mode.")

(defvar mbedtls-test-data-mode-hook nil
  "Normal hook to run when entering Mbed TLS test data mode.")

(defun mbedtls-test-data-mode ()
  "Major mode to edit Mbed TLS test data files.

\\{mbedtls-test-data-mode-map}"
  (interactive)
  (kill-all-local-variables)
  (setq major-mode 'mbedtls-test-data-mode)
  (setq mode-name "MbedTLS")
  (set-syntax-table mbedtls-test-data-mode-syntax-table)
  (setq comment-start "# "
        comment-end "")
  (use-local-map mbedtls-test-data-mode-map)
  (make-variable-buffer-local 'font-lock-defaults)
  (setq font-lock-defaults mbedtls-test-data-mode-font-lock-defaults)
  (mbedtls-test-data-parse-function-file t)
  (run-hooks 'mbedtls-test-data-mode-hook))

(provide 'mbedtls-test-data-mode)

;;; That's all.
