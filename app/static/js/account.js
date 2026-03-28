(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function showAlert(message, type) {
    const container = document.getElementById('alert-container');
    if (!container) return;

    // type: 'success' | 'error'
    const alertClass = type === 'success' ? 'alert-success' : 'alert-error';

    container.innerHTML = `
      <div class="alert ${alertClass}" role="alert">
        <div class="alert-content">
          <p class="alert-message">${message}</p>
        </div>
      </div>
    `;

    // Scroll alert into view
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Auto-dismiss success alerts after 5 seconds
    if (type === 'success') {
      setTimeout(function () {
        const existing = container.querySelector('.alert');
        if (existing) existing.remove();
      }, 5000);
    }
  }

  // ---------------------------------------------------------------------------
  // Change password form
  // ---------------------------------------------------------------------------

  const passwordForm = document.getElementById('change-password-form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async function (e) {
      e.preventDefault();

      const currentPassword = document.getElementById('current-password').value.trim();
      const newPassword = document.getElementById('new-password').value.trim();
      const confirmPassword = document.getElementById('confirm-password').value.trim();

      if (!currentPassword || !newPassword || !confirmPassword) {
        showAlert('Please fill in all password fields.', 'error');
        return;
      }

      if (newPassword !== confirmPassword) {
        showAlert('New passwords do not match.', 'error');
        return;
      }

      if (newPassword.length < 8) {
        showAlert('New password must be at least 8 characters.', 'error');
        return;
      }

      const submitBtn = passwordForm.querySelector('button[type="submit"]');
      submitBtn.disabled = true;

      try {
        const res = await fetch('/api/auth/password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword
          })
        });

        const data = await res.json().catch(function () { return {}; });

        if (res.ok) {
          showAlert('Password updated successfully.', 'success');
          passwordForm.reset();
        } else {
          showAlert(data.detail || 'Failed to update password. Please check your current password and try again.', 'error');
        }
      } catch (err) {
        showAlert('Network error. Please try again.', 'error');
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Delete account modal
  // ---------------------------------------------------------------------------

  const deleteBtn = document.getElementById('delete-account-btn');
  const deleteModal = document.getElementById('delete-modal');
  const deleteModalBackdrop = document.getElementById('delete-modal-backdrop');
  const deleteModalCancel = document.getElementById('delete-modal-cancel');
  const deleteModalConfirm = document.getElementById('delete-modal-confirm');

  function showModal() {
    if (deleteModal) {
      deleteModal.style.display = 'flex';
      deleteModal.classList.add('is-visible');
    }
  }

  function hideModal() {
    if (deleteModal) {
      deleteModal.classList.remove('is-visible');
      deleteModal.style.display = 'none';
    }
  }

  if (deleteBtn) {
    deleteBtn.addEventListener('click', showModal);
  }

  if (deleteModalCancel) {
    deleteModalCancel.addEventListener('click', hideModal);
  }

  if (deleteModalBackdrop) {
    deleteModalBackdrop.addEventListener('click', hideModal);
  }

  if (deleteModalConfirm) {
    deleteModalConfirm.addEventListener('click', async function () {
      deleteModalConfirm.disabled = true;

      try {
        const res = await fetch('/api/auth/delete-account', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });

        if (res.ok) {
          window.location.href = '/';
        } else {
          const data = await res.json().catch(function () { return {}; });
          hideModal();
          showAlert(data.detail || 'Failed to delete account. Please try again.', 'error');
        }
      } catch (err) {
        hideModal();
        showAlert('Network error. Please try again.', 'error');
      } finally {
        deleteModalConfirm.disabled = false;
      }
    });
  }

  // Close modal on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && deleteModal && deleteModal.style.display !== 'none') {
      hideModal();
    }
  });

})();
