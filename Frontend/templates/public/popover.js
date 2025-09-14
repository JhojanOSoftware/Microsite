(function () {
      const pop = document.getElementById('skill-popover');

      function showPopover(target, text) {
        pop.textContent = text;
        pop.setAttribute('aria-hidden', 'false');
        pop.classList.add('visible');

        const rect = target.getBoundingClientRect();
        const popRect = pop.getBoundingClientRect();
        const margin = 12;

        // preferred position: above the element, otherwise below
        let top = rect.top - popRect.height - margin;
        if (top < 70) { // account for navbar height
          top = rect.bottom + margin;
        }
        let left = rect.left + (rect.width / 2) - (popRect.width / 2);

        // keep within viewport
        left = Math.max(12, Math.min(left, window.innerWidth - popRect.width - 12));

        pop.style.top = (top + window.scrollY) + 'px';
        pop.style.left = (left + window.scrollX) + 'px';

        // remember last target for focus
        pop.dataset.anchorId = target.dataset.skillId || '';
      }

      function hidePopover() {
        pop.setAttribute('aria-hidden', 'true');
        pop.classList.remove('visible');
        pop.textContent = '';
      }

      // attach to skill items
      document.querySelectorAll('.skills ul li').forEach((li, idx) => {
        li.dataset.skillId = 'skill-' + idx;
        li.addEventListener('click', (e) => {
          const desc = li.getAttribute('data-desc') || 'Sin descripción';
          showPopover(li, desc);
        });
        li.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            li.click();
          }
        });
      });

      // close on outside click or Escape
      document.addEventListener('click', (e) => {
        const insideSkill = e.target.closest('.skills ul li');
        const insidePop = e.target.closest('#skill-popover');
        if (!insideSkill && !insidePop) hidePopover();
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') hidePopover();
      });

      // reposition on resize/scroll
      window.addEventListener('resize', hidePopover);
      window.addEventListener('scroll', () => {
        if (pop.classList.contains('visible')) hidePopover();
      });
    })();