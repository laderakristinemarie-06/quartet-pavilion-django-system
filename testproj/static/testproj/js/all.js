  /* ── Room data ── */
    const rooms = {
      sr: {
        photos: [
          { src: 'img/SR1.jpg', alt: 'Superior Room – Bedroom' },
          { src: 'img/SR2.jpg', alt: 'Superior Room – Lounge Area' },
          { src: 'img/SR3.jpg', alt: 'Superior Room – Bathroom' },
        ],
        cards: [
          { label: 'Room Type',   value: 'Superior Room' },
          { label: 'Capacity',    value: '2 Guests' },
          { label: 'Bed Size',    value: 'Queen' },
          { label: 'Room Size',   value: '28 sqm' },
          { label: 'View',        value: 'Garden' },
          { label: 'Rate / Night', value: '₱ 4,800' },
        ],
        eyebrow:  'Superior Room',
        heading:  'Comfort Crafted with Provençal Warmth',
        body:     'The Superior Room offers a refined retreat for those who appreciate thoughtful comfort. Dressed in warm linens, earthy tones, and garden-facing windows, each detail has been chosen to welcome you into restful ease.',
        rate:     '₱ 4,800',
        amenities: [
          'Queen-size bed with premium linen',
          'Private en-suite bathroom',
          'Air conditioning & ceiling fan',
          'Complimentary breakfast for 2',
          'Garden terrace access',
          'Free high-speed Wi-Fi',
          'Flat-screen TV & minibar',
        ],
      },
      dr: {
        photos: [
          { src: 'img/DR1.jpg', alt: 'Deluxe Room – Bedroom' },
          { src: 'img/DR2.jpg', alt: 'Deluxe Room – Sitting Area' },
          { src: 'img/DR3.jpg', alt: 'Deluxe Room – Bathroom' },
        ],
        cards: [
          { label: 'Room Type',   value: 'Deluxe Room' },
          { label: 'Capacity',    value: '2–3 Guests' },
          { label: 'Bed Size',    value: 'King' },
          { label: 'Room Size',   value: '42 sqm' },
          { label: 'View',        value: 'Garden & Pool' },
          { label: 'Rate / Night', value: '₱ 6,500' },
        ],
        eyebrow:  'Deluxe Room',
        heading:  'Expansive Luxury in Every Corner',
        body:     'The Deluxe Room invites you into a larger, more indulgent space. A king-size bed, generous sitting area, and sweeping views of the garden and pool make it the ideal choice for guests seeking something truly memorable.',
        rate:     '₱ 6,500',
        amenities: [
          'King-size bed with luxury linen',
          'Spacious private bathroom with soaking tub',
          'Air conditioning, ceiling fan & heated floors',
          'Complimentary breakfast for 2',
          'Private balcony with garden & pool view',
          'Free high-speed Wi-Fi',
          'Flat-screen TV, minibar & Nespresso machine',
          'Evening turndown service',
        ],
      },
    };

    let activeRoom = 'sr';
    let activePhoto = 0;

    /* ── Render photo ── */
    function renderPhoto(room, index) {
      const photo = rooms[room].photos[index];
      const img   = document.getElementById('roomPhoto');
      const dots  = document.getElementById('photoDots');

      img.classList.add('fade');
      setTimeout(() => {
        img.src = photo.src;
        img.alt = photo.alt;
        img.classList.remove('fade');
      }, 300);

      // Rebuild dots
      dots.innerHTML = '';
      rooms[room].photos.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = 'photo-dot' + (i === index ? ' photo-dot--active' : '');
        dot.addEventListener('click', () => { activePhoto = i; renderPhoto(activeRoom, i); });
        dots.appendChild(dot);
      });
    }

    /* ── Render detail cards ── */
    function renderCards(room) {
      const grid = document.getElementById('roomDetails');
      grid.innerHTML = rooms[room].cards.map(c => `
        <div class="room-card">
          <span class="room-card__label">${c.label}</span>
          <span class="room-card__value">${c.value}</span>
        </div>`).join('');
    }

    /* ── Render right panel ── */
    function renderPanel(room) {
      const d = rooms[room];
      document.getElementById('rpEyebrow').textContent  = d.eyebrow;
      document.getElementById('rpHeading').textContent  = d.heading;
      document.getElementById('rpBody').textContent     = d.body;
      document.getElementById('rpRate').textContent     = d.rate;

      const list = document.getElementById('rpAmenities');
      list.innerHTML = d.amenities.map(a =>
        `<li class="amenity-list__item">${a}</li>`
      ).join('');
    }

    /* ── Full render ── */
    function render(room) {
      activeRoom  = room;
      activePhoto = 0;
      renderPhoto(room, 0);
      renderCards(room);
      renderPanel(room);

      document.querySelectorAll('.room-tab').forEach(btn => {
        btn.classList.toggle('room-tab--active', btn.dataset.room === room);
        btn.setAttribute('aria-selected', btn.dataset.room === room ? 'true' : 'false');
      });
    }

    /* ── Tab clicks ── */
    document.querySelectorAll('.room-tab').forEach(btn => {
      btn.addEventListener('click', () => render(btn.dataset.room));
    });

    /* ── Arrow clicks ── */
    document.getElementById('photoPrev').addEventListener('click', () => {
      const len = rooms[activeRoom].photos.length;
      activePhoto = (activePhoto - 1 + len) % len;
      renderPhoto(activeRoom, activePhoto);
    });

    document.getElementById('photoNext').addEventListener('click', () => {
      const len = rooms[activeRoom].photos.length;
      activePhoto = (activePhoto + 1) % len;
      renderPhoto(activeRoom, activePhoto);
    });

    /* ── Init ── */
    render('sr');