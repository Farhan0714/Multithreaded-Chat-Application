console.log('🚀 ZetaChat Pro initializing...');

if (window.zetaChatInitialized) {
  console.log('⚠️ Already initialized, skipping...');
} else {
  window.zetaChatInitialized = true;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
  } else {
    initializeApp();
  }
}

function initializeApp() {
  console.log('🎯 Starting app initialization...');

  const socket = window.chatSocket || io();
  window.chatSocket = socket;

  const dashboard = document.getElementById('dashboard');
  const chat = document.getElementById('chat');
  const loginScreen = document.getElementById('loginScreen');
  const registerScreen = document.getElementById('registerScreen');
  const forgotPasswordScreen = document.getElementById('forgotPasswordScreen');
  const showRegisterBtn = document.getElementById('showRegister');
  const showLoginBtn = document.getElementById('showLogin');
  const showForgotPassword = document.getElementById('showForgotPassword');
  const backToLogin = document.getElementById('backToLogin');

  const loginEmailInput = document.getElementById('loginEmail');
  const loginPasswordInput = document.getElementById('loginPassword');
  const loginBtn = document.getElementById('loginBtn');

  const regEmailInput = document.getElementById('regEmail');
  const sendOtpBtn = document.getElementById('sendOtpBtn');
  const otpSection = document.getElementById('otpSection');
  const otpInput = document.getElementById('otpInput');
  const verifyOtpBtn = document.getElementById('verifyOtpBtn');

  const regProfilePicInput = document.getElementById('regProfilePic');
  const regProfilePicPreview = document.getElementById('regProfilePicPreview');
  const continueToStep3Btn = document.getElementById('continueToStep3');
  const backToStep1Btn = document.getElementById('backToStep1');
  const backToStep2Btn = document.getElementById('backToStep2');

  const regUsernameInput = document.getElementById('regUsername');
  const regPasswordInput = document.getElementById('regPassword');
  const regConfirmPasswordInput = document.getElementById('regConfirmPassword');
  const registerBtn = document.getElementById('registerBtn');

  const forgotEmail = document.getElementById('forgotEmail');
  const sendResetCodeBtn = document.getElementById('sendResetCodeBtn');
  const forgotStep1 = document.getElementById('forgotStep1');
  const forgotStep2 = document.getElementById('forgotStep2');
  const resetCodeInput = document.getElementById('resetCodeInput');
  const newPasswordInput = document.getElementById('newPasswordInput');
  const confirmNewPasswordInput = document.getElementById('confirmNewPasswordInput');
  const resetPasswordBtn = document.getElementById('resetPasswordBtn');

  let currentStep = 1;
  let verifiedEmail = null;
  let selectedProfilePic = null;

  const sidebar = document.querySelector('.sidebar');
  const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
  const closeSidebarBtn = document.getElementById('closeSidebarBtn');
  const sidebarOverlay = document.querySelector('.sidebar-overlay');
  const usersList = document.getElementById('usersList');
  const roomsList = document.getElementById('roomsList');
  const messages = document.getElementById('messages');
  const messageInput = document.getElementById('messageInput');
  const sendBtn = document.getElementById('sendBtn');
  const emojiBtn = document.getElementById('emojiBtn');
  const attachBtn = document.getElementById('attachBtn');
  const photoBtn = document.getElementById('photoBtn');
  const videoBtn = document.getElementById('videoBtn');
  const voiceRecordBtn = document.getElementById('voiceRecordBtn');
  const fileInput = document.getElementById('fileInput');
  const photoInput = document.getElementById('photoInput');
  const videoInput = document.getElementById('videoInput');
  const themeToggle = document.getElementById('themeToggle');
  const myName = document.getElementById('myName');
  const myProfilePic = document.getElementById('myProfilePic');
  const chatWith = document.getElementById('chatWith');
  const chatStatus = document.getElementById('chatStatus');
  const typingIndicator = document.getElementById('typingIndicator');

  const voiceCallBtn = document.getElementById('voiceCallBtn');
  const videoCallBtn = document.getElementById('videoCallBtn');
  const callContainer = document.getElementById('callContainer');
  const callStatus = document.getElementById('callStatus');
  const callTimer = document.getElementById('callTimer');
  const endCallBtn = document.getElementById('endCallBtn');
  const toggleMuteBtn = document.getElementById('toggleMuteBtn');
  const toggleVideoBtn = document.getElementById('toggleVideoBtn');
  const localVideo = document.getElementById('localVideo');
  const remoteVideo = document.getElementById('remoteVideo');
  const videoContainer = document.getElementById('videoContainer');
  const gamesModal = document.getElementById('gamesModal');

  let currentUser = null;
  let currentRoom = 'global';
  let isVerified = false;
  let isDarkTheme = localStorage.getItem('theme') === 'dark';
  let isRecording = false;
  let mediaRecorder = null;
  let audioChunks = [];
  let typingTimeout = null;
  let savedRooms = {};
  let sidebarOpen = window.innerWidth > 768;

  let localStream = null;
  let peerConnection = null;
  let isInCall = false;
  let callTimerInterval = null;
  let callStartTime = null;
  let currentCallId = null;
  let isMuted = false;
  let isVideoEnabled = true;
  let remotePeerSid = null;
  let callInitiator = false;

  if (isDarkTheme) {
    document.body.setAttribute('data-theme', 'dark');
    if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
  }

  initForgotPassword();

  createRoomButton();

  function initForgotPassword() {
    if (!showForgotPassword) return;

    showForgotPassword.onclick = (e) => {
      e.preventDefault();
      loginScreen.classList.add('hidden');
      forgotPasswordScreen.classList.remove('hidden');
      forgotStep1.classList.remove('hidden');
      forgotStep2.classList.add('hidden');
    };

    if (backToLogin) {
      backToLogin.onclick = (e) => {
        e.preventDefault();
        forgotPasswordScreen.classList.add('hidden');
        loginScreen.classList.remove('hidden');
        forgotEmail.value = '';
        resetCodeInput.value = '';
        newPasswordInput.value = '';
        confirmNewPasswordInput.value = '';
      };
    }

    if (sendResetCodeBtn) {
      sendResetCodeBtn.onclick = async (e) => {
        e.preventDefault();
        const email = forgotEmail.value.trim().toLowerCase();

        if (!email || !isValidEmail(email)) {
          showNotification('Please enter a valid email address', 'error');
          return;
        }

        sendResetCodeBtn.disabled = true;
        sendResetCodeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

        try {
          const response = await fetch('/api/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
          });

          const data = await response.json();

          if (data.success) {
            forgotStep1.classList.add('hidden');
            forgotStep2.classList.remove('hidden');
            showNotification('Reset code sent to your email!', 'success');
          } else {
            showNotification(data.error || 'Failed to send reset code', 'error');
          }
        } catch (error) {
          showNotification('Failed to send reset code', 'error');
        } finally {
          sendResetCodeBtn.disabled = false;
          sendResetCodeBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Reset Code';
        }
      };
    }

    if (resetPasswordBtn) {
      resetPasswordBtn.onclick = async (e) => {
        e.preventDefault();
        const email = forgotEmail.value.trim().toLowerCase();
        const otp = resetCodeInput.value.trim();
        const newPassword = newPasswordInput.value;
        const confirmPassword = confirmNewPasswordInput.value;

        if (!otp || otp.length !== 6) {
          showNotification('Please enter the 6-digit code', 'error');
          return;
        }

        if (!newPassword || newPassword.length < 6) {
          showNotification('Password must be at least 6 characters', 'error');
          return;
        }

        if (newPassword !== confirmPassword) {
          showNotification('Passwords do not match', 'error');
          return;
        }

        resetPasswordBtn.disabled = true;
        resetPasswordBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Resetting...';

        try {
          const response = await fetch('/api/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email,
              otp,
              new_password: newPassword
            })
          });

          const data = await response.json();

          if (data.success) {
            showNotification('Password reset successfully! Please login', 'success');
            setTimeout(() => {
              forgotPasswordScreen.classList.add('hidden');
              loginScreen.classList.remove('hidden');
              forgotEmail.value = '';
              resetCodeInput.value = '';
              newPasswordInput.value = '';
              confirmNewPasswordInput.value = '';
              forgotStep1.classList.remove('hidden');
              forgotStep2.classList.add('hidden');
            }, 1500);
          } else {
            showNotification(data.error || 'Password reset failed', 'error');
          }
        } catch (error) {
          showNotification('Password reset failed', 'error');
        } finally {
          resetPasswordBtn.disabled = false;
          resetPasswordBtn.innerHTML = '<i class="fas fa-check-circle"></i> Reset Password';
        }
      };
    }
  }

  function createRoomButton() {
    const createRoomBtn = document.createElement('button');
    createRoomBtn.innerHTML = '<i class="fas fa-plus"></i> Create Room';
    createRoomBtn.className = 'btn-secondary create-room-btn';
    createRoomBtn.onclick = showCreateRoomModal;

    if (roomsList && roomsList.parentElement) {
      const roomsSection = roomsList.closest('.rooms-section');
      if (roomsSection) {
        const sectionHeader = roomsSection.querySelector('.section-header');
        if (sectionHeader && sectionHeader.nextElementSibling) {
          roomsSection.insertBefore(createRoomBtn, sectionHeader.nextElementSibling);
        }
      }
    }
  }

  function showStep(stepNum) {
    document.querySelectorAll('.reg-step').forEach(step => step.classList.remove('active'));
    document.querySelectorAll('.step').forEach((step, index) => {
      if (index + 1 < stepNum) {
        step.classList.add('completed');
        step.classList.remove('active');
      } else if (index + 1 === stepNum) {
        step.classList.add('active');
        step.classList.remove('completed');
      } else {
        step.classList.remove('active', 'completed');
      }
    });

    document.getElementById(`step${stepNum}`).classList.add('active');
    currentStep = stepNum;
  }

  if (showRegisterBtn) {
    showRegisterBtn.onclick = (e) => {
      e.preventDefault();
      loginScreen.classList.add('hidden');
      registerScreen.classList.remove('hidden');
      showStep(1);
    };
  }

  if (showLoginBtn) {
    showLoginBtn.onclick = (e) => {
      e.preventDefault();
      registerScreen.classList.add('hidden');
      loginScreen.classList.remove('hidden');
    };
  }

  if (sendOtpBtn) {
    sendOtpBtn.onclick = async (e) => {
      e.preventDefault();
      const email = regEmailInput.value.trim().toLowerCase();

      if (!email || !isValidEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
      }

      sendOtpBtn.disabled = true;
      sendOtpBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

      try {
        const response = await fetch('/api/send-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.success) {
          otpSection.classList.remove('hidden');
          showNotification('Verification code sent to your email!', 'success');
        } else {
          showNotification(data.error || 'Failed to send verification code', 'error');
        }
      } catch (error) {
        showNotification('Failed to send verification code', 'error');
      } finally {
        sendOtpBtn.disabled = false;
        sendOtpBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Verification Code';
      }
    };
  }

  if (verifyOtpBtn) {
    verifyOtpBtn.onclick = async (e) => {
      e.preventDefault();
      const email = regEmailInput.value.trim().toLowerCase();
      const otp = otpInput.value.trim();

      if (!otp || otp.length !== 6) {
        showNotification('Please enter the 6-digit code', 'error');
        return;
      }

      verifyOtpBtn.disabled = true;
      verifyOtpBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';

      try {
        const response = await fetch('/api/verify-otp', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, otp })
        });

        const data = await response.json();

        if (data.verified) {
          verifiedEmail = email;
          showNotification('Email verified successfully!', 'success');
          setTimeout(() => showStep(2), 500);
        } else {
          showNotification(data.message || 'Invalid verification code', 'error');
        }
      } catch (error) {
        showNotification('Verification failed', 'error');
      } finally {
        verifyOtpBtn.disabled = false;
        verifyOtpBtn.innerHTML = '<i class="fas fa-check-circle"></i> Verify Email';
      }
    };
  }

  if (regProfilePicInput) {
    regProfilePicInput.onchange = async (e) => {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          regProfilePicPreview.src = e.target.result;
          continueToStep3Btn.disabled = false;
        };
        reader.readAsDataURL(file);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', 'profile');

        try {
          showNotification('Uploading profile picture...', 'info');
          const response = await fetch('/api/upload', { method: 'POST', body: formData });
          const data = await response.json();
          if (data.file_path) {
            selectedProfilePic = data.file_path;
            showNotification('Profile picture uploaded!', 'success');
          }
        } catch (error) {
          showNotification('Failed to upload profile picture', 'error');
        }
      }
    };
  }

  if (backToStep1Btn) {
    backToStep1Btn.onclick = () => showStep(1);
  }

  if (continueToStep3Btn) {
    continueToStep3Btn.onclick = () => {
      if (!selectedProfilePic) {
        showNotification('Please upload a profile picture', 'error');
        return;
      }
      showStep(3);
    };
  }

  if (backToStep2Btn) {
    backToStep2Btn.onclick = () => showStep(2);
  }

  if (registerBtn) {
    registerBtn.onclick = async (e) => {
      e.preventDefault();

      const username = regUsernameInput.value.trim();
      const password = regPasswordInput.value;
      const confirmPassword = regConfirmPasswordInput.value;

      if (!username || !password || !confirmPassword) {
        showNotification('Please fill all fields', 'error');
        return;
      }

      if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        return;
      }

      if (password.length < 6) {
        showNotification('Password must be at least 6 characters', 'error');
        return;
      }

      if (!verifiedEmail) {
        showNotification('Email not verified', 'error');
        showStep(1);
        return;
      }

      if (!selectedProfilePic) {
        showNotification('Profile picture not uploaded', 'error');
        showStep(2);
        return;
      }

      registerBtn.disabled = true;
      registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';

      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: verifiedEmail,
            username,
            password,
            profile_pic: selectedProfilePic
          })
        });

        const data = await response.json();

        if (data.success) {
          showNotification('Account created successfully! Please login', 'success');
          setTimeout(() => {
            registerScreen.classList.add('hidden');
            loginScreen.classList.remove('hidden');
            regEmailInput.value = '';
            otpInput.value = '';
            regUsernameInput.value = '';
            regPasswordInput.value = '';
            regConfirmPasswordInput.value = '';
            regProfilePicPreview.src = '/static/img/default-avatar.png';
            otpSection.classList.add('hidden');
            verifiedEmail = null;
            selectedProfilePic = null;
            showStep(1);
          }, 1500);
        } else {
          showNotification(data.error || 'Registration failed', 'error');
        }
      } catch (error) {
        showNotification('Registration failed', 'error');
      } finally {
        registerBtn.disabled = false;
        registerBtn.innerHTML = '<i class="fas fa-user-plus"></i> Create Account';
      }
    };
  }

  if (loginBtn) {
    loginBtn.onclick = async (e) => {
      e.preventDefault();
      const email = loginEmailInput.value.trim().toLowerCase();
      const password = loginPasswordInput.value;

      if (!email || !password) {
        showNotification('Please enter email and password', 'error');
        return;
      }

      if (!isValidEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
      }

      loginBtn.disabled = true;
      loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';

      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
          currentUser = data.username;
          selectedProfilePic = data.profile_pic;
          isVerified = data.is_verified;

          dashboard.classList.remove('active');
          dashboard.classList.add('hidden');
          chat.classList.remove('hidden');
          chat.classList.add('active');

          if (myName) myName.textContent = currentUser;
          if (myProfilePic) myProfilePic.src = getProfilePicUrl(selectedProfilePic);

          socket.emit('join', {
            username: currentUser,
            email: email,
            profile_pic: selectedProfilePic,
            is_verified: isVerified
          });

          showNotification('Welcome to ZetaChat Pro! 🎉', 'success');
        } else {
          showNotification(data.error || 'Invalid credentials', 'error');
        }
      } catch (error) {
        showNotification('Login failed', 'error');
      } finally {
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Login';
      }
    };
  }

  if (loginPasswordInput) {
    loginPasswordInput.onkeypress = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        loginBtn.click();
      }
    };
  }

  function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  function formatTime(timestamp) {
    if (!timestamp) {
      const now = new Date();
      return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }
    return timestamp;
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function getProfilePicUrl(profilePic) {
    if (!profilePic) return '/static/img/default-avatar.png';
    if (profilePic.startsWith('http')) return profilePic;
    if (profilePic.startsWith('/')) return profilePic;
    return `/uploads/${profilePic}`;
  }

  function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
  }

  function toggleSidebar() {
    if (window.innerWidth <= 768) {
      sidebar.classList.toggle('show');
      if (sidebar.classList.contains('show')) {
        sidebarOverlay.style.display = 'block';
      } else {
        sidebarOverlay.style.display = 'none';
      }
    } else {
      sidebarOpen = !sidebarOpen;
      if (sidebarOpen) {
        sidebar.style.transform = 'translateX(0)';
        sidebar.style.marginLeft = '0';
      } else {
        sidebar.style.transform = 'translateX(-100%)';
        sidebar.style.marginLeft = '-380px';
      }
    }
  }

  if (toggleSidebarBtn) {
    toggleSidebarBtn.onclick = toggleSidebar;
  }

  if (closeSidebarBtn) {
    closeSidebarBtn.onclick = () => {
      sidebar.classList.remove('show');
      sidebarOverlay.style.display = 'none';
    };
  }

  if (sidebarOverlay) {
    sidebarOverlay.onclick = () => {
      sidebar.classList.remove('show');
      sidebarOverlay.style.display = 'none';
    };
  }

  if (themeToggle) {
    themeToggle.onclick = () => {
      isDarkTheme = !isDarkTheme;
      document.body.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
      themeToggle.innerHTML = isDarkTheme ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
      localStorage.setItem('theme', isDarkTheme ? 'dark' : 'light');
    };
  }

  if (messageInput) {
    messageInput.oninput = () => {
      if (sendBtn) sendBtn.disabled = messageInput.value.trim().length === 0;
      messageInput.style.height = 'auto';
      messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';

      if (messageInput.value.trim().length > 0) {
        socket.emit('typing', { room: currentRoom, typing: true });
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
          socket.emit('typing', { room: currentRoom, typing: false });
        }, 1000);
      }
    };

    messageInput.onkeydown = (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    };

    messageInput.onfocus = () => {
      if (window.innerWidth <= 768) {
        setTimeout(() => {
          messageInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 300);
      }
    };
  }

  if (sendBtn) {
    sendBtn.onclick = sendMessage;
  }

  function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    socket.emit('message', {
      username: currentUser,
      room: currentRoom,
      message: message,
      type: 'text'
    });

    messageInput.value = '';
    messageInput.style.height = 'auto';
    if (sendBtn) sendBtn.disabled = true;
    socket.emit('typing', { room: currentRoom, typing: false });
  }

  if (photoBtn && photoInput) {
    photoBtn.onclick = () => photoInput.click();
    photoInput.onchange = async (e) => {
      const files = Array.from(e.target.files);
      for (const file of files) {
        if (file.type.startsWith('image/')) {
          await uploadAndSendFile(file, 'photo');
        }
      }
      photoInput.value = '';
    };
  }

  if (videoBtn && videoInput) {
    videoBtn.onclick = () => videoInput.click();
    videoInput.onchange = async (e) => {
      const files = Array.from(e.target.files);
      for (const file of files) {
        if (file.type.startsWith('video/')) {
          await uploadAndSendFile(file, 'video');
        }
      }
      videoInput.value = '';
    };
  }

  if (attachBtn && fileInput) {
    attachBtn.onclick = () => fileInput.click();
    fileInput.onchange = async (e) => {
      const files = Array.from(e.target.files);
      for (const file of files) {
        await uploadAndSendFile(file, 'file');
      }
      fileInput.value = '';
    };
  }

  async function uploadAndSendFile(file, type) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    try {
      showNotification('Uploading...', 'info');
      const response = await fetch('/api/upload', { method: 'POST', body: formData });
      const data = await response.json();

      if (data.file_path) {
        let messageType = type;
        if (file.type.startsWith('image/')) messageType = 'image';
        else if (file.type.startsWith('video/')) messageType = 'video';
        else if (file.type.startsWith('audio/')) messageType = 'voice';

        socket.emit('message', {
          username: currentUser,
          room: currentRoom,
          message: file.name,
          type: messageType,
          file_path: data.file_path,
          file_name: file.name,
          file_size: data.file_size
        });
        showNotification('Uploaded!', 'success');
      }
    } catch (error) {
      showNotification('Upload failed', 'error');
    }
  }

  if (voiceRecordBtn) {
    voiceRecordBtn.onmousedown = startRecording;
    voiceRecordBtn.onmouseup = stopRecording;
    voiceRecordBtn.ontouchstart = startRecording;
    voiceRecordBtn.ontouchend = stopRecording;
  }

  async function startRecording() {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('Media recording not supported on this device', 'error');
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const file = new File([audioBlob], `voice_${Date.now()}.webm`, { type: 'audio/webm' });
        await uploadAndSendFile(file, 'voice');
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      isRecording = true;
      voiceRecordBtn.innerHTML = '<i class="fas fa-stop"></i>';
      showNotification('🎤 Recording...', 'info');
    } catch (error) {
      showNotification('Could not access microphone', 'error');
    }
  }

  function stopRecording() {
    if (isRecording && mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      isRecording = false;
      voiceRecordBtn.innerHTML = '<i class="fas fa-microphone"></i>';
    }
  }

  if (voiceCallBtn) {
    voiceCallBtn.onclick = () => startCall('voice');
  }

  if (videoCallBtn) {
    videoCallBtn.onclick = () => startCall('video');
  }

  async function startCall(callType) {
    try {
      if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        showNotification('Voice/Video calls require HTTPS. Please use HTTPS or localhost.', 'error');
        return;
      }

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showNotification('Your browser does not support media devices. Try Chrome or Safari.', 'error');
        return;
      }

      const constraints = {
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        },
        video: callType === 'video' ? {
          facingMode: 'user',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } : false
      };
      localStream = await navigator.mediaDevices.getUserMedia(constraints);

      if (callContainer) callContainer.classList.remove('hidden');
      if (callType === 'video' && videoContainer && localVideo) {
        videoContainer.classList.remove('hidden');
        localVideo.srcObject = localStream;
        if (toggleVideoBtn) toggleVideoBtn.classList.remove('hidden');
      }

      if (callStatus) callStatus.textContent = 'Calling...';
      callInitiator = true;
      socket.emit('start_call', { room: currentRoom, call_type: callType });
      showNotification(`Starting ${callType} call...`, 'info');
    } catch (error) {
      showNotification('Could not start call: ' + error.message, 'error');
      console.error('Call error:', error);
    }
  }

  function setupPeerConnection(targetSid) {
    const configuration = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
      ]
    };
    peerConnection = new RTCPeerConnection(configuration);

    if (localStream) {
      localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream);
      });
    }

    peerConnection.ontrack = (event) => {
      console.log('📺 Received remote track');
      if (remoteVideo && event.streams[0]) {
        remoteVideo.srcObject = event.streams[0];
        if (callStatus) callStatus.textContent = 'Connected';
        isInCall = true;
        startCallTimer();
      }
    };

    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        socket.emit('ice_candidate', {
          target_sid: targetSid,
          candidate: event.candidate,
          call_id: currentCallId
        });
      }
    };

    peerConnection.onconnectionstatechange = () => {
      console.log('Connection state:', peerConnection.connectionState);
      if (peerConnection.connectionState === 'disconnected' ||
          peerConnection.connectionState === 'failed') {
        endCall();
      }
    };

    remotePeerSid = targetSid;
  }

  if (endCallBtn) {
    endCallBtn.onclick = endCall;
  }

  function endCall() {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      localStream = null;
    }
    if (peerConnection) {
      peerConnection.close();
      peerConnection = null;
    }
    if (callContainer) callContainer.classList.add('hidden');
    if (videoContainer) videoContainer.classList.add('hidden');
    if (callTimerInterval) {
      clearInterval(callTimerInterval);
      callTimerInterval = null;
    }

    if (currentCallId) {
      socket.emit('end_call', { call_id: currentCallId });
    }

    isInCall = false;
    callInitiator = false;
    remotePeerSid = null;
    currentCallId = null;
    showNotification('Call ended', 'info');
  }

  function startCallTimer() {
    callStartTime = Date.now();
    callTimerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
      const minutes = Math.floor(elapsed / 60);
      const seconds = elapsed % 60;
      if (callTimer) {
        callTimer.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
      }
    }, 1000);
  }

  if (toggleMuteBtn) {
    toggleMuteBtn.onclick = () => {
      if (localStream) {
        const audioTrack = localStream.getAudioTracks()[0];
        if (audioTrack) {
          audioTrack.enabled = !audioTrack.enabled;
          isMuted = !audioTrack.enabled;
          toggleMuteBtn.innerHTML = isMuted ? '<i class="fas fa-microphone-slash"></i>' : '<i class="fas fa-microphone"></i>';
        }
      }
    };
  }

  if (toggleVideoBtn) {
    toggleVideoBtn.onclick = () => {
      if (localStream) {
        const videoTrack = localStream.getVideoTracks()[0];
        if (videoTrack) {
          videoTrack.enabled = !videoTrack.enabled;
          toggleVideoBtn.innerHTML = videoTrack.enabled ? '<i class="fas fa-video"></i>' : '<i class="fas fa-video-slash"></i>';
        }
      }
    };
  }

  function showCreateRoomModal() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h2><i class="fas fa-door-open"></i> Create New Room</h2>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="input-group">
            <label>Room Name *</label>
            <input type="text" id="newRoomName" placeholder="Enter room name" />
          </div>
          <div class="input-group">
            <label>Description</label>
            <textarea id="newRoomDesc" placeholder="What's this room about?" rows="3"></textarea>
          </div>
          <div class="checkbox-group">
            <label class="checkbox-label">
              <input type="checkbox" id="isPrivateRoom" />
              <span> Make this a private room (requires 6-digit code to join)</span>
            </label>
          </div>
          <button id="createRoomSubmit" class="btn-primary" style="margin-top: 20px;">
            <i class="fas fa-plus-circle"></i> Create Room
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector('.modal-close').onclick = () => modal.remove();
    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };

    document.getElementById('createRoomSubmit').onclick = () => {
      const name = document.getElementById('newRoomName').value.trim();
      const desc = document.getElementById('newRoomDesc').value.trim();
      const isPrivate = document.getElementById('isPrivateRoom').checked;

      if (!name) {
        showNotification('Please enter a room name', 'error');
        return;
      }

      socket.emit('create_room', {
        name: name,
        description: desc,
        is_private: isPrivate
      });

      modal.remove();
    };
  }

  function renderMessage(msg) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.dataset.messageId = msg.id;

    const isOwnMessage = msg.username === currentUser;

    if (msg.type === 'system') {
      messageDiv.classList.add('system');
      messageDiv.innerHTML = `<div class="message-bubble">${escapeHtml(msg.message)}</div>`;
    } else if (msg.type === 'ai') {
      messageDiv.classList.add('received');
      messageDiv.innerHTML = `
        <div class="message-avatar"><img src="/static/img/default-avatar.png" alt="AI" /></div>
        <div class="message-bubble" style="background: linear-gradient(135deg, #667eea, #764ba2); color: white;">
          <div class="message-username" style="color: rgba(255,255,255,0.9);">🤖 AI Assistant</div>
          <div class="message-text">${escapeHtml(msg.message)}</div>
          <div class="message-footer">
            <span class="message-time" style="color: rgba(255,255,255,0.7);">${formatTime(msg.timestamp)}</span>
          </div>
        </div>
      `;
    } else {
      messageDiv.classList.add(isOwnMessage ? 'sent' : 'received');
      const profilePic = getProfilePicUrl(msg.profile_pic);
      let contentHtml = '';

      if (msg.type === 'image') {
        contentHtml = `<img src="${msg.file_path}" alt="Image" onclick="window.open('${msg.file_path}','_blank')" style="max-width:300px;border-radius:8px;cursor:pointer;margin:4px 0;" />`;
      } else if (msg.type === 'video') {
        contentHtml = `<video controls style="max-width:300px;border-radius:8px;margin:4px 0;"><source src="${msg.file_path}" type="video/mp4"></video>`;
      } else if (msg.type === 'voice') {
        contentHtml = `<div style="min-width:250px;"><audio controls style="width:100%;"><source src="${msg.file_path}" type="audio/webm"></audio></div>`;
      } else if (msg.type === 'file') {
        contentHtml = `
          <div style="display:flex;align-items:center;gap:10px;padding:12px;background:var(--bg-tertiary);border-radius:8px;">
            <i class="fas fa-file" style="font-size:24px;color:var(--primary);"></i>
            <div style="flex:1;">
              <a href="${msg.file_path}" download="${escapeHtml(msg.file_name || msg.message)}" style="color:var(--text-primary);text-decoration:none;font-weight:600;">
                ${escapeHtml(msg.file_name || msg.message)}
              </a>
              ${msg.file_size ? `<div style="font-size:11px;color:var(--text-secondary);">${formatFileSize(msg.file_size)}</div>` : ''}
            </div>
          </div>
        `;
      } else {
        contentHtml = `<div class="message-text">${escapeHtml(msg.message)}</div>`;
      }

      const translateBtn = msg.type === 'text' ? `
        <button class="translate-btn" onclick="translateMessage(${msg.id}, '${escapeHtml(msg.message).replace(/'/g, "\\'")}')"
                style="background:none;border:none;color:var(--primary);cursor:pointer;font-size:12px;margin-left:8px;">
          <i class="fas fa-language"></i>
        </button>
      ` : '';

      messageDiv.innerHTML = `
        ${!isOwnMessage ? `<div class="message-avatar"><img src="${profilePic}" alt="${escapeHtml(msg.username)}" /></div>` : ''}
        <div class="message-bubble">
          ${!isOwnMessage ? `<div class="message-username">${escapeHtml(msg.username)}</div>` : ''}
          ${contentHtml}
          <div class="message-footer">
            <span class="message-time">${formatTime(msg.timestamp)}</span>
            ${translateBtn}
          </div>
        </div>
        ${isOwnMessage ? `<div class="message-avatar"><img src="${getProfilePicUrl(selectedProfilePic)}" alt="You" /></div>` : ''}
      `;
    }

    if (messages) {
      messages.appendChild(messageDiv);
      messages.scrollTop = messages.scrollHeight;
    }
  }

  window.translateMessage = async function(messageId, text) {
    const langs = ['fr', 'es', 'de', 'hi', 'zh', 'ja', 'ar', 'en'];
    const langNames = {
      'fr': 'French', 'es': 'Spanish', 'de': 'German', 'hi': 'Hindi',
      'zh': 'Chinese', 'ja': 'Japanese', 'ar': 'Arabic', 'en': 'English'
    };

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <div class="modal-header">
          <h2><i class="fas fa-language"></i> Translate Message</h2>
          <button class="modal-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="input-group">
            <label>Select Target Language</label>
            <select id="targetLang" style="width:100%;padding:12px;border-radius:8px;border:2px solid var(--border);background:var(--bg-tertiary);color:var(--text-primary);">
              ${langs.map(lang => `<option value="${lang}">${langNames[lang]}</option>`).join('')}
            </select>
          </div>
          <div style="margin-top:20px;">
            <strong>Original:</strong>
            <div style="padding:12px;background:var(--bg-tertiary);border-radius:8px;margin-top:8px;">${escapeHtml(text)}</div>
          </div>
          <div style="margin-top:20px;">
            <strong>Translation:</strong>
            <div id="translationResult" style="padding:12px;background:var(--bg-tertiary);border-radius:8px;margin-top:8px;min-height:50px;">
              <div class="spinner"></div>
            </div>
          </div>
          <button id="translateBtn" class="btn-primary" style="margin-top:20px;">
            <i class="fas fa-sync"></i> Translate
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    modal.querySelector('.modal-close').onclick = () => modal.remove();
    modal.onclick = (e) => {
      if (e.target === modal) modal.remove();
    };

    document.getElementById('translateBtn').onclick = async () => {
      const targetLang = document.getElementById('targetLang').value;
      const resultDiv = document.getElementById('translationResult');
      resultDiv.innerHTML = '<div class="spinner"></div>';

      try {
        const response = await fetch('/api/translate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text, target_lang: targetLang })
        });
        const data = await response.json();
        if (data.success) {
          resultDiv.innerHTML = escapeHtml(data.translated);
        } else {
          resultDiv.innerHTML = '<span style="color:var(--danger);">Translation failed</span>';
        }
      } catch (error) {
        resultDiv.innerHTML = '<span style="color:var(--danger);">Translation error</span>';
      }
    };

    setTimeout(() => document.getElementById('translateBtn').click(), 100);
  };

  socket.off();

  socket.on('join_success', (data) => {
    currentRoom = data.room;
    if (data.saved_rooms) {
      savedRooms = data.saved_rooms;
    }
    showNotification('Connected!', 'success');
  });

  socket.on('rooms_list', (rooms) => {
    if (!roomsList) return;
    roomsList.innerHTML = '';
    rooms.forEach(room => {
      const div = document.createElement('div');
      div.classList.add('room-item');
      if (room.id === currentRoom) div.classList.add('active');
      div.innerHTML = `
        <i class="fas fa-${room.is_private ? 'lock' : 'hashtag'}"></i>
        <div>
          <div>${escapeHtml(room.name)}</div>
          ${room.description ? `<small style="color:var(--text-secondary)">${escapeHtml(room.description)}</small>` : ''}
        </div>
      `;
      div.onclick = () => {
        if (room.is_private && !savedRooms[room.id]) {
          const code = prompt('🔐 Enter 6-digit room code:');
          if (code && code.length === 6) {
            socket.emit('join_room', { room_id: room.id, code: code });
          }
        } else {
          socket.emit('join_room', { room_id: room.id });
        }
      };
      roomsList.appendChild(div);
    });
  });

  socket.on('users_update', (users) => {
    if (!usersList) return;
    usersList.innerHTML = '';
    users.forEach(user => {
      if (user.username !== currentUser) {
        const li = document.createElement('li');
        li.classList.add('user-item');
        li.innerHTML = `
          <div class="user-avatar">
            <img src="${getProfilePicUrl(user.profile_pic)}" alt="${escapeHtml(user.username)}" />
          </div>
          <div class="user-info">
            <div class="user-name">${escapeHtml(user.username)}</div>
            <div class="user-last-seen">${user.status || 'online'}</div>
          </div>
        `;
        li.onclick = () => socket.emit('start_private', { target: user.username });
        usersList.appendChild(li);
      }
    });
  });

  socket.on('message', (msg) => {
    renderMessage(msg);
  });

  socket.on('message_history', (history) => {
    if (messages) messages.innerHTML = '';
    history.forEach(renderMessage);
  });

  socket.on('message_blocked', (data) => {
    showNotification(data.message, 'error');
  });

  socket.on('typing', (data) => {
    if (typingIndicator) {
      if (data.typing) {
        typingIndicator.innerHTML = `<img src="${getProfilePicUrl(data.profile_pic)}" style="width:16px;height:16px;border-radius:50%;margin-right:4px;" /> ${escapeHtml(data.username)} is typing...`;
      } else {
        typingIndicator.textContent = '';
      }
    }
  });

  socket.on('room_joined', (data) => {
    currentRoom = data.room_id;
    savedRooms[data.room_id] = {
      name: data.room_name,
      is_private: data.is_private,
      code: data.is_private ? 'saved' : null
    };
    if (chatWith) chatWith.textContent = data.room_name;
    if (chatStatus) chatStatus.textContent = data.is_private ? '🔒 Private Room' : '🌐 Public Room';
    if (messages) messages.innerHTML = '';
    showNotification(`Joined ${data.room_name}`, 'success');

    if (window.innerWidth <= 768) {
      sidebar.classList.remove('show');
      sidebarOverlay.style.display = 'none';
    }
  });

  socket.on('room_created', (data) => {
    if (data.is_private && data.code) {
      const modal = document.createElement('div');
      modal.className = 'modal';
      modal.innerHTML = `
        <div class="modal-content">
          <div class="modal-header">
            <h2><i class="fas fa-check-circle"></i> Room Created!</h2>
            <button class="modal-close">&times;</button>
          </div>
          <div class="modal-body" style="text-align:center;">
            <div style="font-size:3rem;margin:20px 0;">🔐</div>
            <h3 style="margin-bottom:10px;">${escapeHtml(data.room_name)}</h3>
            <p style="color:var(--text-secondary);margin-bottom:20px;">Private Room Created Successfully!</p>
            <div style="background:var(--bg-tertiary);padding:20px;border-radius:12px;margin:20px 0;">
              <p style="margin-bottom:10px;font-weight:600;">Room Code:</p>
              <div style="font-size:2rem;font-weight:bold;color:var(--primary);letter-spacing:8px;font-family:monospace;">
                ${data.code}
              </div>
              <p style="margin-top:10px;font-size:14px;color:var(--text-secondary);">Share this code with others to let them join!</p>
            </div>
            <button class="btn-primary" onclick="navigator.clipboard.writeText('${data.code}');alert('Code copied!')">
              <i class="fas fa-copy"></i> Copy Code
            </button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);
      modal.querySelector('.modal-close').onclick = () => modal.remove();
      modal.onclick = (e) => {
        if (e.target === modal) modal.remove();
      };
    } else {
      showNotification(`Room "${data.room_name}" created!`, 'success');
    }
  });

  socket.on('private_started', (data) => {
    currentRoom = data.room;
    if (chatWith) chatWith.textContent = data.partner;
    if (chatStatus) chatStatus.textContent = '💬 Private Chat';
    if (messages) messages.innerHTML = '';

    if (window.innerWidth <= 768) {
      sidebar.classList.remove('show');
      sidebarOverlay.style.display = 'none';
    }
  });

  socket.on('user_status_change', (data) => {
    const userItem = Array.from(document.querySelectorAll('.user-item')).find(
      item => item.querySelector('.user-name') && item.querySelector('.user-name').textContent === data.username
    );
    if (userItem) {
      const statusEl = userItem.querySelector('.user-last-seen');
      if (data.status === 'online') {
        statusEl.textContent = 'online';
        statusEl.style.color = 'var(--success)';
      } else {
        statusEl.textContent = `Last seen ${data.last_seen}`;
        statusEl.style.color = 'var(--text-secondary)';
      }
    }
  });

  socket.on('user_online_notification', (data) => {
    showNotification(`${data.username} is now online! 🟢`, 'success');
  });

  socket.on('incoming_call', async (data) => {
    console.log('📞 Incoming call from:', data.from);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      showNotification('Media devices not supported on this device', 'error');
      socket.emit('answer_call', {
        call_id: data.call_id,
        answer: false
      });
      return;
    }

    const accept = confirm(`📞 Incoming ${data.call_type} call from ${data.from}. Accept?`);

    if (accept) {
      currentCallId = data.call_id;

      try {
        const constraints = { audio: true, video: data.call_type === 'video' };
        localStream = await navigator.mediaDevices.getUserMedia(constraints);

        if (callContainer) callContainer.classList.remove('hidden');
        if (data.call_type === 'video' && videoContainer && localVideo) {
          videoContainer.classList.remove('hidden');
          localVideo.srcObject = localStream;
          if (toggleVideoBtn) toggleVideoBtn.classList.remove('hidden');
        }

        setupPeerConnection(data.caller_sid);

        socket.emit('answer_call', {
          call_id: data.call_id,
          answer: true
        });

        if (callStatus) callStatus.textContent = 'Connecting...';
      } catch (error) {
        showNotification('Could not access media devices', 'error');
        socket.emit('answer_call', {
          call_id: data.call_id,
          answer: false
        });
      }
    } else {
      socket.emit('answer_call', {
        call_id: data.call_id,
        answer: false
      });
    }
  });

  socket.on('call_answered', async (data) => {
    console.log('📞 Call answered:', data);

    if (data.answer) {
      if (callInitiator) {
        setupPeerConnection(data.answerer_sid);

        try {
          const offer = await peerConnection.createOffer();
          await peerConnection.setLocalDescription(offer);

          socket.emit('webrtc_offer', {
            target_sid: data.answerer_sid,
            offer: offer,
            call_id: data.call_id
          });

          if (callStatus) callStatus.textContent = 'Connecting...';
        } catch (error) {
          console.error('Error creating offer:', error);
          showNotification('Call setup failed', 'error');
        }
      }
    } else {
      showNotification('Call rejected', 'info');
      endCall();
    }
  });

  socket.on('webrtc_offer', async (data) => {
    console.log('📡 Received offer from:', data.from);

    try {
      if (!peerConnection) {
        setupPeerConnection(data.from_sid);
      }

      await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer));
      const answer = await peerConnection.createAnswer();
      await peerConnection.setLocalDescription(answer);

      socket.emit('webrtc_answer', {
        target_sid: data.from_sid,
        answer: answer,
        call_id: data.call_id
      });
    } catch (error) {
      console.error('Error handling offer:', error);
    }
  });

  socket.on('webrtc_answer', async (data) => {
    console.log('📡 Received answer from:', data.from);

    try {
      await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
    } catch (error) {
      console.error('Error handling answer:', error);
    }
  });

  socket.on('ice_candidate', async (data) => {
    console.log('🧊 Received ICE candidate');

    if (peerConnection && data.candidate) {
      try {
        await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
      } catch (error) {
        console.error('Error adding ICE candidate:', error);
      }
    }
  });

  socket.on('call_ended', () => {
    showNotification('Call ended', 'info');
    endCall();
  });

  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.onclick = () => btn.closest('.modal').classList.add('hidden');
  });

  document.querySelectorAll('.modal').forEach(modal => {
    modal.onclick = (e) => {
      if (e.target === modal) modal.classList.add('hidden');
    };
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
      sidebar.classList.remove('show');
      sidebarOverlay.style.display = 'none';
      if (sidebarOpen) {
        sidebar.style.transform = 'translateX(0)';
      }
    }
  });

  const viewportMeta = document.querySelector('meta[name="viewport"]');
  if (viewportMeta) {
    viewportMeta.setAttribute('content', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');
  }

  function showNotification(message, type = 'info') {
    console.log(`🔔 ${type.toUpperCase()}: ${message}`);
    const notification = document.createElement('div');
    notification.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i> ${message}`;
    notification.style.cssText = `
      position: fixed; top: 20px; right: 20px; padding: 16px 24px;
      background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
      color: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 9999; display: flex; align-items: center; gap: 10px; font-weight: 500;
      animation: slideInRight 0.3s ease-out; max-width: 400px;
    `;
    document.body.appendChild(notification);
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
}