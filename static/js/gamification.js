/**
 * Kinesis AI — Gamification & Badge Unlock Celebrations
 */

function triggerBadgeUnlockCelebration(badge) {
    const modalHtml = `
        <div class="modal fade" id="badgeUnlockModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content bg-dark text-light border border-warning text-center p-4">
                    <div class="display-1 mb-2">${badge.badge_icon || '🏆'}</div>
                    <h3 class="text-warning fw-bold mb-1">Badge Unlocked!</h3>
                    <h5 class="text-light fw-bold">${badge.badge_name}</h5>
                    <p class="text-secondary small mb-3">${badge.badge_description}</p>
                    <div class="badge bg-warning text-dark fs-6 py-2 px-3 mb-4">+${badge.xp_reward || 50} XP Awarded</div>
                    <button type="button" class="btn btn-outline-light rounded-pill px-4" data-bs-dismiss="modal">Awesome!</button>
                </div>
            </div>
        </div>
    `;

    // Remove existing if any
    const old = document.getElementById('badgeUnlockModal');
    if (old) old.remove();

    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modalEl = document.getElementById('badgeUnlockModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
    KinesisAudio.playRepTone();
}
