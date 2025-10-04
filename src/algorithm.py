import torch
import torch.nn as nn

# constants / hyperparameters
LEARNING_RATE = 1e-6
NUM_EPOCHS = 1000

# the actual algorithm thats doing all the work, but will eventually need to be translated
# into an object so that it can generate predictions on future input data
def algorthm(horses):
    # split input array into two different arrays as idx 7 is the actual results
    x = torch.from_numpy(horses[:, :-1]).float()
    y = torch.from_numpy(horses[:, -1]).float().view(-1, 1)

    model = nn.Sequential(
        nn.Linear(7, 192),
        nn.ReLU(),
        nn.Linear(192, 192),
        nn.ReLU(),
        nn.Linear(192, 1)
    )

    lossFunction = nn.MSELoss(reduction='mean')
    optimizer = torch.optim.RMSprop(model.parameters(), lr=LEARNING_RATE)

    for epoch in range(NUM_EPOCHS):
        y_prediction = model(x)

        loss = lossFunction(y_prediction, y)
        if epoch % 100 == 99:
            print(epoch, loss.item())

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

