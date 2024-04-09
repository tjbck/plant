const getResponse = async (messages) => {
  let error = null;

  const res = await fetch(`http://localhost:5555/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages,
    }),
  })
    .then(async (res) => {
      if (!res.ok) throw await res.json();
      return res.json();
    })
    .catch((err) => {
      console.log(err);
      error = err;
      return null;
    });

  if (error) {
    throw error;
  }

  return res?.response ?? null;
};

module.exports = { getResponse };
