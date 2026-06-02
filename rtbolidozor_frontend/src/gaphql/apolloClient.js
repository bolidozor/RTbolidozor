import { ApolloClient, InMemoryCache } from '@apollo/client/core';
import { createHttpLink } from 'apollo-link-http';

// Vytvoření Apollo Clientu
const httpLink = createHttpLink({
  uri: 'http://localhost:8001/graphql/', // Změňte URL podle vašeho serveru
});

const cache = new InMemoryCache();

const apolloClient = new ApolloClient({
  link: httpLink,
  cache,
});

export default apolloClient;
