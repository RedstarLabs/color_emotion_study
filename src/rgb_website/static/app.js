const EMOTIONS = [
  "Wut",
  "Angst",
  "Freude",
  "Trauer",
  "Überraschung",
  "Verachtung",
  "Ekel",
];

const state = {
  sessionId: null,
  experimentVersion: null,
  color: null,
  trialNumber: 0,
  busy: false,
};

const introView = document.querySelector("#intro-view");
const studyView = document.querySelector("#study-view");
const completeView = document.querySelector("#complete-view");
const startButton = document.querySelector("#start-button");
const genderOptions = document.querySelector("#gender-options");
const introError = document.querySelector("#intro-error");
const globalError = document.querySelector("#global-error");
const studyMessage = document.querySelector("#study-message");
const abandonButton = document.querySelector("#abandon-button");
const progressLabel = document.querySelector("#progress-label");
const colorSwatch = document.querySelector("#color-swatch");
const emotionOptions = document.querySelector("#emotion-options");

function show(view) {
  introView.hidden = view !== introView;
  studyView.hidden = view !== studyView;
  completeView.hidden = view !== completeView;
}

function setMessage(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("error", isError);
  element.hidden = !message;
}

function apiError(response) {
  if (response.status === 404) {
    return "Dieser Versuch wurde nicht gefunden.";
  }
  if (response.status === 409) {
    return "Diese Antwort passt nicht mehr zum aktuellen Versuch.";
  }
  return "Die Anfrage konnte nicht verarbeitet werden.";
}

async function abandonStudy() {
  if (state.busy || !state.sessionId) {
    return;
  }
  state.busy = true;
  setButtonsDisabled(true);
  abandonButton.disabled = true;
  setMessage(studyMessage, "Studie wird abgebrochen …");
  try {
    await request(
      `/api/experiments/${encodeURIComponent(state.sessionId)}/abandon`,
      { method: "POST" },
    );
    show(introView);
    setMessage(
      introError,
      "Der unvollständige Versuch wurde beendet. Es wurden keine fehlenden Antworten ergänzt.",
    );
  } catch (error) {
    setMessage(studyMessage, error.message, true);
    setButtonsDisabled(false);
    abandonButton.disabled = false;
  } finally {
    state.busy = false;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new Error("Netzwerkfehler. Bitte prüfen Sie Ihre Verbindung und versuchen Sie es erneut.");
  }

  if (!response.ok) {
    throw new Error(apiError(response));
  }

  let payload;
  try {
    payload = await response.json();
  } catch {
    throw new Error("Die Antwort des Servers war ungültig.");
  }
  return payload;
}

function renderState(payload) {
  if (
    typeof payload.session_id !== "string" ||
    typeof payload.status !== "string" ||
    typeof payload.answered_count !== "number" ||
    typeof payload.total_count !== "number"
  ) {
    throw new Error("Die Antwort des Servers war unvollständig.");
  }

  state.sessionId = payload.session_id;
  state.experimentVersion = payload.experiment_version;
  state.trialNumber = payload.answered_count + 1;
  state.color = payload.next_color;
  setButtonsDisabled(false);
  abandonButton.disabled = false;

  if (payload.status === "completed" || payload.next_color === null) {
    show(completeView);
    return;
  }

  const { red, green, blue, position, id } = payload.next_color;
  if (
    typeof id !== "string" ||
    ![red, green, blue, position].every((value) => Number.isInteger(value))
  ) {
    throw new Error("Die Farbinformation des Servers war ungültig.");
  }

  progressLabel.textContent = `Farbe ${position} von ${payload.total_count}`;
  colorSwatch.style.backgroundColor = `rgb(${red}, ${green}, ${blue})`;
  colorSwatch.setAttribute("aria-label", `Studienfarbe ${position} von ${payload.total_count}`);
  setMessage(studyMessage, "");
  show(studyView);
}

function setButtonsDisabled(disabled) {
  emotionOptions.querySelectorAll("button").forEach((button) => {
    button.disabled = disabled;
  });
}

async function startStudy() {
  if (state.busy) {
    return;
  }
  state.busy = true;
  startButton.disabled = true;
  setMessage(introError, "");
  try {
    const selectedGender = document.querySelector(
      'input[name="gender"]:checked',
    );
    const payload = await request("/api/experiments", {
      method: "POST",
      body: JSON.stringify({
        gender: selectedGender ? selectedGender.value : "not_specified",
      }),
    });
    renderState(payload);
  } catch (error) {
    setMessage(introError, error.message, true);
    startButton.disabled = false;
  } finally {
    state.busy = false;
  }
}

async function submitEmotion(emotion) {
  if (state.busy || !state.sessionId || !state.color) {
    return;
  }
  state.busy = true;
  setButtonsDisabled(true);
  setMessage(studyMessage, "Antwort wird gespeichert …");
  try {
    const payload = await request(
      `/api/experiments/${encodeURIComponent(state.sessionId)}/responses`,
      {
        method: "POST",
        body: JSON.stringify({
          color_id: state.color.id,
          emotion,
          trial_number: state.trialNumber,
          experiment_version: state.experimentVersion,
        }),
      },
    );
    renderState(payload);
  } catch (error) {
    const answeredBeforeRecovery = state.trialNumber - 1;
    try {
      const currentState = await request(
        `/api/experiments/${encodeURIComponent(state.sessionId)}`,
      );
      renderState(currentState);
      if (currentState.answered_count > answeredBeforeRecovery) {
        setMessage(
          studyMessage,
          "Die Antwort wurde gespeichert. Der aktuelle Stand wurde geladen.",
        );
      } else {
        setMessage(studyMessage, error.message, true);
      }
    } catch {
      setMessage(
        studyMessage,
        `${error.message} Bitte versuchen Sie dieselbe Auswahl erneut.`,
        true,
      );
      setButtonsDisabled(false);
    }
  } finally {
    state.busy = false;
  }
}

function renderEmotionButtons() {
  EMOTIONS.forEach((emotion) => {
    const button = document.createElement("button");
    button.className = "emotion-button";
    button.type = "button";
    button.textContent = emotion;
    button.addEventListener("click", () => submitEmotion(emotion));
    emotionOptions.append(button);
  });
}

startButton.addEventListener("click", startStudy);
abandonButton.addEventListener("click", abandonStudy);
renderEmotionButtons();
